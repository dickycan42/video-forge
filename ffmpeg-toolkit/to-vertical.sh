#!/bin/bash
# Convert ke vertikal 9:16 1080x1920 (crop tengah)
# Usage: ./to-vertical.sh input.mp4 output.mp4
ffmpeg -y -i "$1" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p" -c:a aac -b:a 128k "$2"
echo "Done: $2"
