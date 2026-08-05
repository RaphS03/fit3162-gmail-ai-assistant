#!/usr/bin/env bash
# PROTOTYPE — THROWAWAY. Spike #84. Local baseline for the companion page.
# localhost counts as a secure context, so getUserMedia is available.
set -e
cd "$(dirname "$0")"
echo "Run 0 — local baseline. Open http://localhost:8084/companion/"
echo "Click buttons 1-3. If the mic fails HERE, it is your browser, not the add-on."
python3 -m http.server 8084
