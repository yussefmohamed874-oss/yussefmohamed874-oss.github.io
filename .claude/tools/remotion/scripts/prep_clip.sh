#!/usr/bin/env bash
# Normalise footage for Remotion: 1080x1920, 30fps, H.264, AAC. Originals are never touched.
# usage: scripts/prep_clip.sh <input.mp4> <name>   -> public/clips/<name>.mp4
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
in="$1"; name="$2"; out="$here/public/clips/$name.mp4"
mkdir -p "$here/public/clips"
ffmpeg -y -v error -i "$in" \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p,setsar=1" \
  -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$out"
echo "$out"
