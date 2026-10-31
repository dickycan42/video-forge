#!/bin/bash
# Normalisasi audio ke -14 LUFS (standar konten)
# Usage: ./loudnorm.sh input.mp4 output.mp4
ffmpeg -y -i "$1" -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:v copy "$2"
echo "Done: $2"
