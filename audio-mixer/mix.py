#!/usr/bin/env python3
"""Multi-track audio mixer: voice + background music + SFX.

Usage:
    python3 mix.py --voice narration.mp3 --music bgm.mp3 \\
        --music-vol 0.19 --sfx sfx.mp3 --sfx-vol 0.7 \\
        --output final_audio.mp3

    # Voice only + music:
    python3 mix.py --voice narration.mp3 --music bgm.mp3 --output out.mp3

Levels (dari pengalaman produksi):
    - Voice: 1.0 (reference, dinormalisasi dulu ke -14 LUFS)
    - Music: 0.19 (~-12dB di bawah voice)
    - SFX: 0.7 (di bawah voice tapi di atas musik)

Music di-loop otomatis ngikutin durasi voice.
Output: loudnorm -14 LUFS + faststart-ready.
"""
import argparse, subprocess, json

def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True)
    ap.add_argument("--music", default=None)
    ap.add_argument("--music-vol", type=float, default=0.19)
    ap.add_argument("--sfx", default=None)
    ap.add_argument("--sfx-vol", type=float, default=0.7)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    voice_dur = probe_duration(a.voice)
    inputs = ["-i", a.voice]
    fc_parts = []
    amix_inputs = ["[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[voice]"]

    idx = 1
    if a.music:
        inputs += ["-stream_loop", "-1", "-i", a.music]
        fc_parts.append(
            f"[{idx}:a]volume={a.music_vol},aloop=loop=-1:size=2e9[bgm]")
        amix_inputs.append("[bgm]")
        idx += 1
    if a.sfx:
        inputs += ["-i", a.sfx]
        fc_parts.append(f"[{idx}:a]volume={a.sfx_vol}[sfx]")
        amix_inputs.append("[sfx]")
        idx += 1

    # Mix all (longest = voice duration via -shortest)
    n = len(amix_inputs)
    fc_parts.append(
        f"{''.join(amix_inputs)}amix=inputs={n}:duration=shortest:dropout_transition=0[mixed]")
    # Final loudnorm on mixed output
    fc_parts.append("[mixed]loudnorm=I=-14:TP=-1.5:LRA=11[out]")

    cmd = (["ffmpeg", "-y"] + inputs +
           ["-filter_complex", ";".join(fc_parts),
            "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k",
            "-t", str(voice_dur), a.output])
    subprocess.run(cmd, check=True)
    print(f"Done: {a.output} ({voice_dur:.1f}s)")

if __name__ == "__main__":
    main()
