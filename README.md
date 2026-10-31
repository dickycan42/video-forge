# Video Forge 🔨

Toolkit produksi video LENGKAP untuk konten kreator. Dari teks naskah sampai video siap posting.

## Modul

### 1. FFmpeg Toolkit (`ffmpeg-toolkit/`)
Script siap pakai untuk operasi video:
| Script | Fungsi |
|--------|--------|
| `concat.sh` | Gabung video jadi satu |
| `subtitle.sh` | Burn subtitle .ass |
| `grade.sh` | Color grading vibrant |
| `loudnorm.sh` | Normalisasi audio -14 LUFS |
| `faststart.sh` | Moov ke depan (buat WA) |
| `to-vertical.sh` | Convert ke 9:16 |
| `info.sh` | Cek durasi/resolusi/loudness |

### 2. TTS Narration (`tts-narration/`)
Teks → audio narasi:
```bash
python3 narrate.py --text "Halo dunia" --voice id-ID-ArdiNeural --output out.mp3
python3 narrate.py --segments segments.json --output out.mp3
```
- Engine: edge-tts (gratis, kualitas bagus) → fallback espeak
- Support per-segmen dengan jeda antar segmen

### 3. Audio Mixer (`audio-mixer/`)
Gabung voice + musik + SFX dengan level yang bener:
```bash
python3 mix.py --voice narration.mp3 --music bgm.mp3 --sfx sfx.mp3 --output final.mp3
```
- Voice: 1.0 (reference) | Musik: 0.19 | SFX: 0.7
- Output: -14 LUFS

### 4. Carousel Generator (`carousel-generator/`)
Teks → slide IG → video:
```bash
python3 carousel.py --slides slides.json --output ./out/
python3 slides-to-video.py --dir ./out/ --output carousel.mp4
```

### 5. Short-Video Pipeline (`short-video-pipeline/`)
Footage + audio → video per platform:
```bash
python3 build.py --footage ./clips/ --audio final.mp3 --platform tiktok --output out.mp4
```
Platform: `tiktok`, `shorts`, `reels`, `yt`, `square`, `fb-reels`, `fb`

### 6. Thumbnail Generator (`thumbnail-generator/`)
```bash
python3 thumb.py --title "JUDUL BESAR" --subtitle "sub" --output thumb.png
```

### 7. Footage Finder (`footage-finder/`)
Cari & download footage stok GRATIS via Pexels API (key gratis, daftar 1 menit di pexels.com/api).
```bash
export PEXELS_API_KEY="key-lu"
python3 footage-finder/find.py --query "outer space" --per-page 5
python3 footage-finder/find.py --query "ocean waves" --download --out ./clips/
```

### 8. Video Generator (`video-generator/`)
Generate video dari prompt teks via Hugging Face API (gratis, butuh token gratis).
```bash
export HF_TOKEN="hf_..."  # gratis di huggingface.co
python3 video-generator/generate.py --prompt "a spaceship flying through nebula" --output clip.mp4
```
Catatan: free tier lambat (5-15 mnt/klip). Untuk hasil cepat, pakai `footage-finder/`.

### 9. ⭐ MASTER PIPELINE (`full-build.py`)
**Satu perintah: naskah teks → video jadi.**
```bash
python3 full-build.py --script naskah.json --footage ./clips/ \
    --music bgm.mp3 --platform tiktok --output final.mp4
```

## Kebutuhan
- Python 3.8+, ffmpeg 5.0+
- `pip install Pillow edge-tts gtts`

### Catatan TTS buat pengguna lain
Modul `tts-narration` otomatis coba 3 engine berurutan:
1. **edge-tts** (suara Microsoft, kualitas terbaik) — `pip install edge-tts`
2. **system tts** (khusus environment Muse)
3. **gTTS** (Google, fallback) — `pip install gtts`

Di komputer biasa, edge-tts langsung jalan tanpa setup tambahan.

## Lisensi
MIT
