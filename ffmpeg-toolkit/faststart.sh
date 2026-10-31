#!/bin/bash
# Pindah moov ke depan (wajib buat kirim WhatsApp)
# Usage: ./faststart.sh input.mp4 output.mp4
ffmpeg -y -i "$1" -c copy -movflags +faststart "$2"
echo "Done: $2"
