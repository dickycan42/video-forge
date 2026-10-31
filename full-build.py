#!/usr/bin/env python3
"""MASTER PIPELINE: teks naskah -> video jadi.

Satu perintah dari naskah teks sampai video siap posting.

Usage:
    python3 full-build.py --script naskah.json --footage ./clips/ \\
        --music bgm.mp3 --platform tiktok --output final.mp4

naskah.json format:
{
    "voice": "id-ID-ArdiNeural",
    "speed": 95,
    "segments": [
        {"text": "Hook yang menarik!", "pause_after": 0.5},
        {"text": "Ini isi videonya.", "pause_after": 0.7}
    ],
    "watermark": "@faktaunikharian",
    "title": "Judul Video"
}

Steps:
    1. TTS: teks -> narration.mp3 (per segmen + jeda)
    2. Mix: voice + music -> final_audio.mp3
    3. Video: footage + final_audio -> video.mp4 (platform preset)
"""
import argparse, json, os, subprocess, sys, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = BASE

def run(cmd, desc):
    print(f"  [{desc}] {' '.join(cmd[:4])}...")
    subprocess.run(cmd, check=True, capture_output=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="naskah.json")
    ap.add_argument("--footage", required=True)
    ap.add_argument("--music", default=None)
    ap.add_argument("--sfx", default=None)
    ap.add_argument("--platform", default="tiktok")
    ap.add_argument("--output", required=True)
    ap.add_argument("--keep-tmp", action="store_true")
    a = ap.parse_args()

    script = json.load(open(a.script))
    tmpdir = tempfile.mkdtemp(prefix="vf_")
    narration = os.path.join(tmpdir, "narration.mp3")
    mixed = os.path.join(tmpdir, "mixed.mp3")
    seg_file = os.path.join(tmpdir, "segments.json")
    json.dump(script["segments"], open(seg_file, "w"))

    print("Step 1/3: TTS narration...")
    run([sys.executable, f"{REPO}/tts-narration/narrate.py",
         "--segments", seg_file,
         "--voice", script.get("voice", "id-ID-ArdiNeural"),
         "--speed", str(script.get("speed", 95)),
         "--output", narration], "TTS")

    print("Step 2/3: Audio mix...")
    mix_cmd = [sys.executable, f"{REPO}/audio-mixer/mix.py",
               "--voice", narration, "--output", mixed]
    if a.music: mix_cmd += ["--music", a.music]
    if a.sfx: mix_cmd += ["--sfx", a.sfx]
    run(mix_cmd, "Mix")

    print("Step 3/3: Video build...")
    vid_cmd = [sys.executable, f"{REPO}/short-video-pipeline/build.py",
               "--footage", a.footage, "--audio", mixed,
               "--platform", a.platform, "--output", a.output]
    if script.get("watermark"):
        vid_cmd += ["--watermark", script["watermark"]]
    run(vid_cmd, "Video")

    if not a.keep_tmp:
        import shutil
        shutil.rmtree(tmpdir)

    print(f"\n✅ DONE: {a.output}")
    if script.get("title"):
        print(f"   Title: {script['title']}")

if __name__ == "__main__":
    main()
