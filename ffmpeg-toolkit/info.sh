#!/bin/bash
# Cek info video: durasi, resolusi, codec, audio, loudness
# Usage: ./info.sh video.mp4
ffprobe -v error \
  -show_entries stream=width,height,codec_name,codec_type,duration,sample_rate \
  -show_entries format=duration,size,bit_rate \
  -of default=noprint_wrappers=1 "$1"
echo "---"
# Cek loudness
ffmpeg -i "$1" -af loudnorm=print_format=json -f null - 2>&1 | \
  python3 -c "
import json,sys,re
m = re.search(r'\{[^}]+\}', sys.stdin.read(), re.S)
if m:
    d = json.loads(m.group(0))
    print(f\"Integrated: {d.get('input_i')} LUFS\")
    print(f\"True Peak: {d.get('input_tp')} dBTP\")
"
