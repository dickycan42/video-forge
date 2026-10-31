#!/usr/bin/env python3
"""Find & download free stock footage via Pexels API (free key).

Setup:
    1. Daftar gratis di https://www.pexels.com/api/ -> dapat API key
    2. Set env: export PEXELS_API_KEY="key-lu"
    3. python3 find.py --query "outer space" --per-page 5
    4. python3 find.py --query "outer space" --download --out ./clips/

Tanpa API key: pakai --demo (scrape halaman search, terbatas).
"""
import argparse, json, os, sys, urllib.request, urllib.parse

API = "https://api.pexels.com/videos/search"

def api_search(query, per_page=5):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        raise RuntimeError("Set PEXELS_API_KEY dulu: export PEXELS_API_KEY='key-lu'")
    req = urllib.request.Request(
        f"{API}?query={urllib.parse.quote(query)}&per_page={per_page}&orientation=portrait",
        headers={"Authorization": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def best_file(video):
    """Pick best MP4 download link."""
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4"]
    if not files:
        return None
    # Prefer HD, reasonable size
    files.sort(key=lambda f: (f.get("width", 0), f.get("height", 0)), reverse=True)
    return files[0]["link"]

def download(url, path):
    print(f"Downloading {path}...")
    urllib.request.urlretrieve(url, path)
    print(f"Done: {path}")

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--query", required=True)
    a.add_argument("--per-page", type=int, default=5)
    a.add_argument("--download", action="store_true")
    a.add_argument("--out", default="./clips")
    args = a.parse_args()

    data = api_search(args.query, args.per_page)
    videos = data.get("videos", [])
    print(f"Found {len(videos)} videos for '{args.query}':\n")
    for i, v in enumerate(videos):
        dur = v.get("duration", "?")
        user = v.get("user", {}).get("name", "?")
        link = best_file(v)
        print(f"[{i}] {dur}s by {user}")
        print(f"    Page: {v.get('url')}")
        if args.download and link:
            os.makedirs(args.out, exist_ok=True)
            ext = ".mp4"
            safe = "".join(c if c.isalnum() else "_" for c in args.query)[:20]
            download(link, f"{args.out}/{safe}_{i}{ext}")

if __name__ == "__main__":
    main()
