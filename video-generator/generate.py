#!/usr/bin/env python3
"""Generate video from text prompt via Hugging Face Inference API (free tier).

Setup:
    1. Daftar gratis di https://huggingface.co -> Settings -> Access Tokens -> buat token
    2. export HF_TOKEN="hf_..."
    3. python3 generate.py --prompt "a spaceship flying through nebula" --output clip.mp4

Model default: Wan-AI/Wan2.1-T2V-1.3B (ringan, lebih cepat di free tier)
Opsi lain: --model genmo/mochi-1-preview

CATATAN JUJUR:
- Free tier HF lambat (5-15 menit/klip) + antri + rate limit ketat
- Kualitas jauh di bawah Veo/Kling/Runway (berbayar)
- Kalo timeout, coba lagi nanti atau pakai footage-finder (Pexels)
"""
import argparse, os, sys, time, json
import urllib.request, urllib.parse

API_BASE = "https://api-inference.huggingface.co/models"

def generate(prompt, model, token, output, timeout=900, poll=15):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}/{model}"
    data = json.dumps({"inputs": prompt}).encode()

    print(f"Generating: '{prompt[:60]}...'")
    print(f"Model: {model}")
    print("Ini bisa makan 5-15 menit di free tier. Tunggu...")

    req = urllib.request.Request(url, data=data, headers=headers)
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                ctype = r.headers.get("Content-Type", "")
                body = r.read()
                # If JSON = still loading or error
                if "application/json" in ctype:
                    j = json.loads(body)
                    if "error" in j:
                        err = j["error"]
                        # Model loading = retry
                        if "loading" in err.lower() or "currently loading" in err.lower():
                            wait = j.get("estimated_time", poll)
                            print(f"Model loading, tunggu {wait:.0f}s...")
                            time.sleep(min(wait + 5, 60))
                            continue
                        raise RuntimeError(f"API error: {err}")
                    print(f"Status: {j}")
                    time.sleep(poll)
                    continue
                # Binary = video!
                with open(output, "wb") as f:
                    f.write(body)
                print(f"\nDone: {output} ({len(body)//1024}KB)")
                return output
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:500]
            if e.code == 503:
                print("Model lagi loading, retry...")
                time.sleep(poll)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}")
    raise TimeoutError("Timeout — coba lagi nanti atau pakai model lebih kecil")

def main():
    a = argparse.ArgumentParser(description="Generate video dari prompt via HF API")
    a.add_argument("--prompt", required=True, help="deskripsi video")
    a.add_argument("--model", default="Wan-AI/Wan2.1-T2V-1.3B",
                   help="model HF (default: Wan2.1 1.3B)")
    a.add_argument("--output", default="generated.mp4")
    a.add_argument("--timeout", type=int, default=900)
    args = a.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("Set HF_TOKEN dulu: export HF_TOKEN='hf_...' (gratis di huggingface.co)")

    generate(args.prompt, args.model, token, args.output, args.timeout)

if __name__ == "__main__":
    main()
