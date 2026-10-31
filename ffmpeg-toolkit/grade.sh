#!/bin/bash
# Color grading vibrant (buat konten anak/ceria)
# Usage: ./grade.sh input.mp4 output.mp4
ffmpeg -y -i "$1" -vf "eq=saturation=1.35:contrast=1.08:brightness=0.03,vibrance=intensity=0.4" -c:a copy "$2"
echo "Done: $2"
