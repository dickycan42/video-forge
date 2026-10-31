#!/usr/bin/env python3
"""Text-to-Speech narration generator.

Supports multiple engines (tries in order):
    1. edge-tts (free, Microsoft voices, ID + EN) - best quality
    2. system tts (/opt/hatch/bin/tts) - for Muse environments
    3. gTTS (Google, free) - fallback

Setup for other users: pip install edge-tts gtts

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

def narrate_system(text, voice, speed, output):
    """Use built-in /opt/hatch/bin/tts (Meta Shortwave API)."""
    # Map voice names: id-ID-ArdiNeural -> avocado_v2:vg_id_m28 (ID male)
    voice_map = {
        "id-ID-ArdiNeural": "avocado_v2:vg_id_m28",
        "id-ID-GadisNeural": "avocado_v2:vg_id_f28",
    }
    sys_voice = voice_map.get(voice, "avocado_v2:vg_id_m28")
    # Detect language from voice
    lang = "id" if voice.startswith("id-") else "en"
    subprocess.run([
        "/opt/hatch/bin/tts", "speak",
        "--text", text,
        "--voice", sys_voice,
        "--language", lang,
        "--speed", str(speed),
        "--format", "mp3",
        "--output", output,
    ], check=True, capture_output=True)

def narrate_gtts(text, output, lang="id"):
    """Google TTS fallback."""
    from gtts import gTTS
    t = gTTS(text, lang=lang)
    t.save(output)

def check_edge_tts():
    try:
        import edge_tts
        return True
    except ImportError:
        return False

async def edge_synthesize(text, voice, rate, output):
    import edge_tts
    rate_str = f"+{rate-100}%" if rate >= 100 else f"{rate-100}%"
    comm = edge_tts.Communicate(text, voice, rate=rate_str)
    await comm.save(output)

def narrate_edge(text, voice, speed, output):
    asyncio.run(edge_synthesize(text, voice, speed, output))

def narrate_segments(segments, voice, speed, output):
    """Synthesize each segment separately, join with pauses."""
    tmpdir = tempfile.mkdtemp()
    parts = []
    use_edge = check_edge_tts()
    for i, seg in enumerate(segments):
        part = os.path.join(tmpdir, f"part{i:03d}.mp3")
        text = seg["text"] if isinstance(seg, dict) else seg
        seg_done = False
        if use_edge:
            try:
                narrate_edge(text, voice, speed, part)
                seg_done = True
            except Exception:
                pass
        if not seg_done:
            try:
                narrate_system(text, voice, speed, part)
                seg_done = True
            except Exception:
                pass
        if not seg_done:
            try:
                lang = "id" if voice.startswith("id-") else "en"
                narrate_gtts(text, part, lang)
                seg_done = True
            except Exception:
                pass
        if not seg_done:
            raise RuntimeError("No TTS engine available")
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
        done = False
        # 1. Try edge-tts
        if check_edge_tts():
            try:
                narrate_edge(text, a.voice, a.speed, a.output)
                done = True
            except Exception as e:
                print(f"edge-tts failed ({e}), trying next", file=sys.stderr)
        # 2. Try system tts
        if not done:
            try:
                narrate_system(text, a.voice, a.speed, a.output)
                done = True
            except Exception as e:
                print(f"system tts failed ({e}), trying next", file=sys.stderr)
        # 3. Try gTTS
        if not done:
            try:
                lang = "id" if a.voice.startswith("id-") else "en"
                narrate_gtts(text, a.output, lang)
                done = True
            except Exception as e:
                print(f"gTTS failed ({e})", file=sys.stderr)
        if not done:
            raise RuntimeError("No TTS engine available. Install: pip install edge-tts gtts")
        print(f"Done: {a.output}")

if __name__ == "__main__":
    main()
