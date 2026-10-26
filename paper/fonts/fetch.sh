#!/usr/bin/env sh
# Download the paper's fonts (OFL, from Google Fonts' repository) into this directory. The font files are gitignored.
#   sh paper/fonts/fetch.sh
set -eu
cd "$(dirname "$0")"
base=https://github.com/google/fonts/raw/main/ofl
for f in OldStandard-Regular OldStandard-Italic OldStandard-Bold; do curl -fsSL -o "$f.ttf" "$base/oldstandardtt/$f.ttf"; done
curl -fsSL -o OFL-OldStandardTT.txt "$base/oldstandardtt/OFL.txt"
curl -fsSL -o IBMPlexMono-Regular.ttf "$base/ibmplexmono/IBMPlexMono-Regular.ttf"
curl -fsSL -o OFL-IBMPlexMono.txt "$base/ibmplexmono/OFL.txt"
echo "fonts ready in $(pwd)"
