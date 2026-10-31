#!/bin/bash
# Burn subtitle .ass ke video
# Usage: ./subtitle.sh input.mp4 subs.ass output.mp4
ffmpeg -y -i "$1" -vf "ass=$2" -c:a copy "$3"
echo "Done: $3"
