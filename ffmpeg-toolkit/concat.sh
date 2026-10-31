#!/bin/bash
# Gabung video jadi satu (semua harus resolusi & codec sama)
# Usage: ./concat.sh output.mp4 input1.mp4 input2.mp4 ...
OUT="$1"; shift
printf "file '%s'\n" "$@" > /tmp/concat_list.txt
ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt -c copy "$OUT"
echo "Done: $OUT"
