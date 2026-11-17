#!/usr/bin/env bash
# Rebuilds the reel editing toolkit in a fresh cloud session (Dr. Youssef El Masry reels).
# Usage: bash tools/reel-toolkit/setup.sh [TOOLKIT_DIR]
# Media assets (Mixkit audio) are re-downloaded from manifest.csv, not stored in this public repo
# (Mixkit license: use in videos is fine, redistribution as standalone files is not).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
T="${1:-$HOME/reel-toolkit}"
mkdir -p "$T"/{fonts,audio,transitions,whisper-small}
cp "$HERE/presets.sh" "$T/"

echo "== Python libs"
pip install -q --break-system-packages faster-whisper pyloudnorm pedalboard opencv-python-headless pillow scipy numpy soundfile

echo "== Node libs (GSAP / lottie / anime). Playwright + Chromium are pre-installed: do not reinstall."
(cd "$T" && mkdir -p node && cd node && [ -f package.json ] || npm init -y >/dev/null; npm install -s gsap@3.12.5 lottie-web@5.12.2 animejs@3.2.2)

echo "== Fonts (Zain is the brand font)"
if [ ! -d "$T/gfonts" ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts "$T/gfonts"
  (cd "$T/gfonts" && git sparse-checkout set ofl/zain ofl/cairo ofl/tajawal ofl/alexandria ofl/readexpro ofl/rubik ofl/montserrat ofl/notonaskharabic)
fi
find "$T/gfonts/ofl" -name '*.ttf' -exec cp {} "$T/fonts/" \;
mkdir -p ~/.fonts && cp "$T"/fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null

echo "== Whisper Small (CTranslate2 int8) from npm, because huggingface.co is blocked"
if [ ! -s "$T/whisper-small/model.bin" ]; then
  W=$(mktemp -d); (cd "$W" && for i in 0 1 2 3; do npm pack -s "@skillninja/shortmovie-telop-model-p$i@1.0.0" >/dev/null; tar -xzf skillninja-shortmovie-telop-model-p$i-1.0.0.tgz && mv package p$i; done
  cp p0/{tokenizer.json,vocabulary.json,config.json,preprocessor_config.json} "$T/whisper-small/"
  cat p0/model.bin.part0 p1/model.bin.part1 p2/model.bin.part2 p3/model.bin.part3 > "$T/whisper-small/model.bin"
  echo "$(cat p0/model.sha256)  $T/whisper-small/model.bin" | sha256sum -c -); rm -rf "$W"
fi

echo "== Mixkit audio library (mixkit.co / assets.mixkit.co must be allowed)"
tail -n +2 "$HERE/manifest.csv" | while IFS=, read -r file cat title id url rest; do
  mkdir -p "$T/audio/$(dirname "$file")"
  [ -s "$T/audio/$file" ] || curl -sSfL "$url" -o "$T/audio/$file" || echo "  failed: $file"
done
cp "$HERE/manifest.csv" "$T/audio/"

echo "== Brand transitions (render with transitions/render.js, then to_rgba.py)"
mkdir -p "$T/transitions/src"
cp "$HERE"/transitions_src/*.html "$T/transitions/src/"
cp "$HERE"/transitions_src/{render.js,to_rgba.py,README.md,cut_frames.json} "$T/transitions/"

echo "Toolkit ready at $T"
