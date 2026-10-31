#!/usr/bin/env python3
"""YouTube thumbnail generator (1280x720).

Usage:
    python3 thumb.py --title "JUDUL BESAR" --subtitle "sub judul" \\
        --bg background.jpg --output thumb.png
    python3 thumb.py --title "JUDUL" --bg-color "#0a1628" --output thumb.png
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720

def get_font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for p in [f"/usr/share/fonts/truetype/dejavu/{name}"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--bg", default=None, help="background image")
    ap.add_argument("--bg-color", default="#0a1628")
    ap.add_argument("--accent", default="#ff8c00", help="accent color")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    if a.bg and os.path.exists(a.bg):
        img = Image.open(a.bg).convert("RGB").resize((W, H))
        # Dark overlay for text readability
        overlay = Image.new("RGB", (W, H), (0, 0, 0))
        img = Image.blend(img, overlay, 0.4)
    else:
        img = Image.new("RGB", (W, H), a.bg_color)

    d = ImageDraw.Draw(img)
    # Accent bar on left
    d.rectangle([0, 0, 20, H], fill=a.accent)

    # Title (max 3 lines, auto-shrink)
    size = 90
    while size > 40:
        f = get_font(size)
        words, lines, line = a.title.split(), [], ""
        for w in words:
            t = f"{line} {w}".strip()
            if d.textbbox((0,0), t, font=f)[2] <= W-120:
                line = t
            else:
                lines.append(line); line = w
        if line: lines.append(line)
        if len(lines) <= 3: break
        size -= 10

    y = (H - len(lines)*int(size*1.2)) // 2 - 20
    for l in lines:
        tw = d.textbbox((0,0), l, font=f)[2]
        x = (W - tw) // 2
        # Shadow
        d.text((x+4, y+4), l, fill="black", font=f)
        d.text((x, y), l, fill="white", font=f)
        y += int(size*1.2)

    if a.subtitle:
        sf = get_font(36, False)
        tw = d.textbbox((0,0), a.subtitle, font=sf)[2]
        d.text(((W-tw)//2, y+20), a.subtitle, fill=a.accent, font=sf)

    img.save(a.output)
    print(f"Done: {a.output}")

if __name__ == "__main__":
    main()
