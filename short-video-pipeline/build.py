#!/usr/bin/env python3
"""Short-video pipeline: footage + narration audio -> finished video.
Supports TikTok, YouTube Shorts, Instagram Reels, etc.

Usage:
    python3 build.py --footage ./clips/ --audio narration.mp3 \\
        --subtitle subs.ass --watermark "@faktaunikharian" --output tiktok.mp4

Steps:
    1. Concat footage clips to match audio duration (loop if needed)
    2. Scale to 720x1280, yuv420p
    3. Mux with narration audio
    4. Burn subtitles (optional)
    5. Add watermark text (optional)
    6. Loudnorm to -14 LUFS + faststart
"""
import argparse, subprocess, glob, os, json

# Platform presets: (width, height, max_duration_sec)
PLATFORMS = {
    "tiktok":   (720, 1280, 180),
    "shorts":   (720, 1280, 180),   # YouTube Shorts (max 3 min)
    "reels":    (720, 1280, 180),   # Instagram Reels
    "yt":       (1280, 720, None),  # YouTube landscape
    "square":   (1080, 1080, None), # Feed square
    "fb-reels": (720, 1280, 180),   # Facebook Reels
    "fb":       (1280, 720, None),  # Facebook feed (landscape)
}

def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--footage", required=True, help="dir with mp4 clips")
    ap.add_argument("--audio", required=True, help="narration mp3/wav")
    ap.add_argument("--subtitle", default=None, help=".ass file (optional)")
    ap.add_argument("--watermark", default=None, help="watermark text (optional)")
    ap.add_argument("--platform", default="tiktok",
                    choices=list(PLATFORMS.keys()),
                    help="target platform (default: tiktok)")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    clips = sorted(glob.glob(os.path.join(a.footage, "*.mp4")))
    assert clips, "No footage clips found"
    audio_dur = probe_duration(a.audio)
    print(f"Audio duration: {audio_dur:.1f}s, {len(clips)} clips")

    # Build concat list, looping until we cover audio duration
    total, lst = 0, []
    with open("/tmp/tk_concat.txt", "w") as f:
        i = 0
        while total < audio_dur:
            c = clips[i % len(clips)]
            f.write(f"file '{c}'\n")
            total += probe_duration(c)
            i += 1
            if i > 50: break  # safety

    pw, ph, max_dur = PLATFORMS[a.platform]
    if max_dur and audio_dur > max_dur:
        print(f"WARNING: audio {audio_dur:.0f}s exceeds {a.platform} max {max_dur}s")
    vf = [f"scale={pw}:{ph}:force_original_aspect_ratio=increase",
          f"crop={pw}:{ph}", "format=yuv420p"]
    if a.subtitle:
        vf.append(f"ass={a.subtitle}")
    if a.watermark:
        safe = a.watermark.replace(":", "\\:")
        vf.append(
            f"drawtext=text='{safe}':fontsize=28:fontcolor=white@0.9:"
            f"x=(w-text_w)/2:y=h-80:shadowcolor=black@0.6:shadowx=2:shadowy=2")
    print(f"Platform: {a.platform} ({pw}x{ph})")

    cmd = ["ffmpeg", "-y",
           "-f", "concat", "-safe", "0", "-i", "/tmp/tk_concat.txt",
           "-i", a.audio,
           "-vf", ",".join(vf),
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart",
           "-threads", "1",
           a.output]
    subprocess.run(cmd, check=True)
    print(f"Done: {a.output}")

if __name__ == "__main__":
    main()
