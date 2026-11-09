#!/usr/bin/env bash
# Downloads every photo the site uses from the current WordPress site into src/images,
# then rebuilds the site so it serves them locally (no dependency on the old site).
set -e
cd "$(dirname "$0")"
python3 build.py >/dev/null            # refresh ../docs/images.txt
mkdir -p images
while read -r url; do
  [ -z "$url" ] && continue
  f="images/$(basename "$url")"
  [ -f "$f" ] || { echo "↓ $f"; curl -fsSL "$url" -o "$f"; }
done < ../docs/images.txt
python3 build.py --local
echo "Done: docs/ now uses local images."
