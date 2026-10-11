#!/usr/bin/env bash
# themeForge's live tour: switch the REAL desktop through every theme (style) in one colour, the way
# themeForge does (hypeforge-theme apply), photograph every screen after each, then put back the
# look that was in use. Logs to themeforge/logs/. Run only when Javier is away or agrees.
set -u
HERE=$(cd "$(dirname "$0")/.." && pwd)
TOOL=~/Programs/forge-suite/hypeforge/applets/theme/hypeforge-theme
COLOUR=${1:-blue}
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="$HERE/logs/live-tour-$STAMP"; mkdir -p "$OUT"
LOG="$OUT/tour.log"; ln -sfn "$OUT" "$HERE/logs/live-tour-latest"
before=$(grep -E '^(style|theme) ' ~/.config/hypeforge/theme/state.toml | sed 's/.*= "\(.*\)"/\1/' | tr '\n' ' ')
echo "before: $before" | tee "$LOG"
for style in windows-11 mac-os-9 kde cosmic macos classic rice; do
  echo "== $style $COLOUR" >>"$LOG"
  $TOOL apply "$style" "$COLOUR" >>"$LOG" 2>&1; echo "exit $?" >>"$LOG"
  sleep 7
  echo "waybar: $(pgrep -x waybar | tr '\n' ' ')  applets: $(ls $XDG_RUNTIME_DIR/hypeforge-*.pid 2>/dev/null | xargs -n1 basename | tr '\n' ' ')" >>"$LOG"
  for o in $(swaymsg -t get_outputs -r | python3 -c "import json,sys;print(' '.join(o['name'] for o in json.load(sys.stdin)))"); do
    grim -o "$o" -s 0.35 "$OUT/$style-$o.png"
  done
done
set -- $before
$TOOL apply "$1" "$2" >>"$LOG" 2>&1
echo "put back: $1 $2 (exit $?)" >>"$LOG"
echo OK >>"$LOG"
