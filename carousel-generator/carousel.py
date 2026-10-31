#!/usr/bin/env python3
"""Generate Instagram carousel slides from JSON.

Usage:
    python3 carousel.py --slides slides.json --output ./out/

slides.json format:
[
    {"header": "PRODUK #1", "headline": "JUDUL BESAR",
     "subtext": "deskripsi...", "price": "Rp50.000", "cta": "GESER →"},
    ...
]
"""
import argparse, json, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BG = (10, 22, 40)
ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)
GRAY = (160, 170, 185)

def get_font(size, bold=True):
    for p in [f"/usr/share/fonts/truetype/dejavu/DejaVuSans-{'' if not bold else 'Bold'}.ttf".replace("-.ttf", ".ttf")]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def centered(draw, text, y, font, fill, max_w=W-120):
    words, lines, line = text.split(), [], ""
    for w in words:
        t = f"{line} {w}".strip()
        if draw.textbbox((0,0), t, font=font)[2] <= max_w:
            line = t
        else:
            lines.append(line); line = w
    if line: lines.append(line)
    for i, l in enumerate(lines):
        tw = draw.textbbox((0,0), l, font=font)[2]
        draw.text(((W-tw)//2, y + i*int(font.size*1.3)), l, fill=fill, font=font)
    return y + len(lines)*int(font.size*1.3)

def pill(draw, text, x, y, font):
    bb = draw.textbbox((0,0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.rounded_rectangle([x, y, x+tw+50, y+th+24], radius=30, fill=ORANGE)
    draw.text((x+25, y+12), text, fill=(20,20,20), font=font)

def make_slide(num, total, s, outdir):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    centered(d, "THE VIRAL VAULT", 80, get_font(32), ORANGE)
    centered(d, "@theviralvault71", 125, get_font(24, False), GRAY)
    pill(d, f"{num}/{total}", W-160, 70, get_font(28))
    d.rectangle([60, 180, W-60, 185], fill=ORANGE)
    y = 240
    if s.get("header"):
        y = centered(d, s["header"], y, get_font(30), ORANGE) + 30
    y = centered(d, s["headline"], y, get_font(62), WHITE) + 25
    if s.get("subtext"):
        y = centered(d, s["subtext"], y, get_font(32, False), ORANGE) + 40
    if s.get("price"):
        f = get_font(48)
        tw = d.textbbox((0,0), s["price"], font=f)[2]
        px = (W-tw)//2 - 30
        d.rounded_rectangle([px, y, px+tw+60, y+80], radius=20, fill=ORANGE)
        d.text((px+30, y+12), s["price"], fill=(20,20,20), font=f)
        y += 120
    if s.get("cta"):
        f = get_font(36)
        tw = d.textbbox((0,0), s["cta"], font=f)[2]
        bx = (W-tw)//2 - 40
        d.rounded_rectangle([bx, H-250, bx+tw+80, H-160], radius=45, fill=ORANGE)
        d.text((bx+40, H-230), s["cta"], fill=(20,20,20), font=f)
    img.save(f"{outdir}/slide-{num}.png")
    print(f"Slide {num}/{total} done")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    os.makedirs(a.output, exist_ok=True)
    slides = json.load(open(a.slides))
    for i, s in enumerate(slides, 1):
        make_slide(i, len(slides), s, a.output)

if __name__ == "__main__":
    main()
