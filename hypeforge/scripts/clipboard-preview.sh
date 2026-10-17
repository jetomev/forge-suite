#!/usr/bin/env bash
# The clipboard panel on a hidden screen, with a FAKE clipboard history (never yours): sample text, a
# link, a path, code, a colour and a picture, stored by cliphist into a throwaway cache folder; the
# "seen" mark into a throwaway state folder. Then panel-preview.py photographs it.
#
#   scripts/clipboard-preview.sh <style> <theme> <out.png> [--panel-args "…"]
set -euo pipefail
cd "$(dirname "$0")/.."
style="${1:-rice}" theme="${2:-kognogos-mocha}" out="${3:-/tmp/clipboard-preview.png}"; shift 3 || true
tmp="$(mktemp -d)"
trap 'rm -rf --one-file-system "$tmp"' EXIT
export XDG_CACHE_HOME="$tmp/cache" XDG_STATE_HOME="$tmp/state"
mkdir -p "$XDG_CACHE_HOME" "$XDG_STATE_HOME"
store() { printf '%s' "$1" | cliphist store; }
python3 -c "from PIL import Image, ImageDraw; im=Image.new('RGB',(640,360),'#1e1e2e'); d=ImageDraw.Draw(im); d.ellipse((220,80,420,280),fill='#cba6f7'); d.rectangle((0,300,640,360),fill='#89b4fa'); im.save('$tmp/pic.png')"
store "Meeting moved to Thursday at 3 pm, bring the printed menus for all four locations."
cliphist store < "$tmp/pic.png"
store "https://github.com/jetomev/forge-suite/issues/54"
store "~/Programs/forge-suite/hypeforge/applets/panels/views/clipboard.py"
store 'def copy_back(entry: str, picture, clip) -> None:'
store "#cba6f7"
store "Thank you for using nogForge!"
python3 scripts/panel-preview.py clipboard --style "$style" --theme "$theme" --out "$out" "$@"
