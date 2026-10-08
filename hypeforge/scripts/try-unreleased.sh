#!/usr/bin/env bash
# Open hypeForge Settings with every Forge app run from its source folder, on the repo's forgekit:
# the versions built 2026-10-08 (forgekit 0.10.0, displayForge 1.1.0, alacrittyForge 1.1.0,
# nogForge 1.4.0, grubForge 2.2.0, bitlaForge 1.1.0, Help & Keys 0.2.0, Settings 0.4.0),
# before any of them is released. Nothing is installed or changed on the system by this script.
set -euo pipefail
P=~/Programs
HF=$P/forge-suite/hypeforge
LOGS=$HF/logs
mkdir -p "$LOGS"
LOG="$LOGS/try-unreleased-$(date +%Y%m%d-%H%M%S).log"
ln -sf "$(basename "$LOG")" "$LOGS/try-unreleased-latest.log"
exec > >(tee "$LOG") 2>&1

PAGES="$LOGS/try-unreleased-pages.toml"
cat > "$PAGES" <<TOML
# Made by scripts/try-unreleased.sh — every page runs from its source folder.
[[page]]
name = "Screens"
command = "python3 $P/forge-suite/displayforge/main.py"
forge = true

[[page]]
name = "Passwords"
command = "sudoforge status; echo; echo 'Press Enter to go back'; read _"

[[page]]
name = "Terminal"
command = "python3 $P/alacrittyforge/main.py"
forge = true

[[page]]
name = "Packages"
command = "python3 $P/nogforge/main.py"
forge = true

[[page]]
name = "Boot Menu"
command = "python3 $P/grubforge/main.py"
forge = true

[[page]]
name = "Mining (test only)"
command = "python3 $P/bitlaforge/main.py"
forge = true

[[page]]
name = "Help & Keys"
command = "$HF/applets/help/hypeforge-help"
forge = true
TOML

echo "hypeForge Settings — trying the unreleased versions ($(date '+%Y-%m-%d %H:%M'))"
echo
for d in forge-suite/forgekit forge-suite/displayforge alacrittyforge nogforge grubforge bitlaforge; do
  printf '  %-26s %s\n' "$d" "$(git -C "$P/$d" log --oneline -1)"
done
echo
echo "Opening Settings in its own window. Close it with Quit at the bottom of the list."
swaymsg exec "env PYTHONPATH=$P/forge-suite/forgekit HYPEFORGE_SETTINGS_PAGES=$PAGES alacritty --class hypeforge-settings -o window.dimensions.columns=130 -o window.dimensions.lines=40 -e $HF/applets/settings/hypeforge-settings" >/dev/null
echo
echo "OK — Settings opened"
