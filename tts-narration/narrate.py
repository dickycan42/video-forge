#!/usr/bin/env python3
"""Text-to-Speech narration generator.

Supports multiple engines (tries in order):
    1. edge-tts (free, good quality, ID + EN voices)
    2. espeak (fallback, robotic)

Usage:
    python3 narrate.py --text "Halo dunia" --voice id-ID-ArdiNeural \\
        --speed 95 --output narration.mp3
    python3 narrate.py --file script.txt --voice en-US-AriaNeural \\
        --output narration.mp3

    # Multiple segments with pauses:
    python3 narrate.py --segments segments.json --output narration.mp3

segments.json format:
[
    {"text": "Hook yang menarik!", "pause_after": 0.5},
    {"text": "Ini bagian kedua.", "pause_after": 0.7}
]
"""
import argparse, asyncio, json, os, subprocess, sys, tempfile

def check_edge_tts():
    try:
        import edge_tts
        return True
    except ImportError:
        return False

async def edge_synthesize(text, voice, rate, output):
    import edge_tts
    # rate: -50% to +50%, convert from speed percent (100 = normal)
    rate_str = f"+{rate-100}%" if rate >= 100 else f"{rate-100}%"
    comm = edge_tts.Communicate(text, voice, rate=rate_str)
    await comm.save(output)

def narrate_edge(text, voice, speed, output):
    asyncio.run(edge_synthesize(text, voice, speed, output))

def narrate_espeak(text, speed, output):
    # espeak fallback: speed in wpm (175 = normal)
    wpm = int(175 * speed / 100)
    wav_tmp = output + ".tmp.wav"
    subprocess.run(["espeak", "-v", "id", "-s", str(wpm),
                    "-w", wav_tmp, text], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", wav_tmp, "-c:a", "libmp3lame",
                    output], check=True, capture_output=True)
    os.remove(wav_tmp)

def narrate_segments(segments, voice, speed, output):
    """Synthesize each segment separately, join with pauses."""
    tmpdir = tempfile.mkdtemp()
    parts = []
    use_edge = check_edge_tts()
    for i, seg in enumerate(segments):
        part = os.path.join(tmpdir, f"part{i:03d}.mp3")
        text = seg["text"] if isinstance(seg, dict) else seg
        if use_edge:
            narrate_edge(text, voice, speed, part)
        else:
            narrate_espeak(text, speed, part)
        parts.append(part)
        pause = seg.get("pause_after", 0.5) if isinstance(seg, dict) else 0.5
        if pause > 0:
            silence = os.path.join(tmpdir, f"sil{i:03d}.mp3")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i",
                 f"anullsrc=r=24000:cl=mono", "-t", str(pause),
                 "-c:a", "libmp3lame", silence],
                check=True, capture_output=True)
            parts.append(silence)
    # Concat all
    lst = os.path.join(tmpdir, "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", output], check=True, capture_output=True)
    print(f"Done: {output} ({len(segments)} segments)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", help="text to narrate")
    ap.add_argument("--file", help="text file to narrate")
    ap.add_argument("--segments", help="JSON file with segments")
    ap.add_argument("--voice", default="id-ID-ArdiNeural",
                    help="voice ID (default: id-ID-ArdiNeural)")
    ap.add_argument("--speed", type=int, default=95,
                    help="speed percent (default: 95)")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    if a.segments:
        segs = json.load(open(a.segments))
        narrate_segments(segs, a.voice, a.speed, a.output)
    else:
        text = a.text or open(a.file).read()
        if check_edge_tts():
            narrate_edge(text, a.voice, a.speed, a.output)
        else:
            print("edge-tts not found, using espeak fallback", file=sys.stderr)
            narrate_espeak(text, a.speed, a.output)
        print(f"Done: {a.output}")

if __name__ == "__main__":
    main()
