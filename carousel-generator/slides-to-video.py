#!/usr/bin/env python3
"""Convert carousel slides to video.

Usage:
    python3 slides-to-video.py --dir ./out/ --duration 2 --output carousel.mp4
"""
import argparse, subprocess, glob, os

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--duration", type=float, default=2)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    slides = sorted(glob.glob(os.path.join(a.dir, "slide-*.png")))
    assert slides, "No slides found"
    fps = f"1/{a.duration}"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", fps, "-i",
        os.path.join(a.dir, "slide-%d.png"),
        "-vf", "scale=1080:1350,format=yuv420p",
        "-c:v", "libx264", "-r", "30", "-crf", "23",
        "-movflags", "+faststart", a.output,
    ], check=True)
    print(f"Done: {a.output} ({len(slides)} slides x {a.duration}s)")

if __name__ == "__main__":
    main()
