#!/usr/bin/env bash
# Uninstall the apps Javier picked on 2026-10-08 (the launcher review): CopyQ, Kvantum, Rofi,
# XTerm/UXTerm, Krusader, KCalc, Elisa. First keep VLC's ffmpeg plugin: Elisa pulled it in, VLC uses
# it, and `nog remove` (pacman -Rs) would take it along. nog has no "keep" command, so that one
# step is plain pacman (strictly needed). Javier runs it: both steps ask for the password.
set -uo pipefail
LOGS=~/Programs/forge-suite/hypeforge/logs
mkdir -p "$LOGS"
LOG="$LOGS/remove-unneeded-apps-$(date +%Y%m%d-%H%M%S).log"
ln -sf "$(basename "$LOG")" "$LOGS/remove-unneeded-apps-latest.log"
exec > >(tee "$LOG") 2>&1

echo "Removing the apps picked in the launcher review ($(date '+%Y-%m-%d %H:%M'))"
echo
echo "Step 1 of 2 · keep VLC's ffmpeg plugin (marked as installed on purpose)"
sudo pacman -D --asexplicit vlc-plugin-ffmpeg || { echo "Step 1 stopped: nothing was removed."; exit 1; }
echo
echo "Step 2 of 2 · uninstall through nog"
nog remove copyq kvantum rofi xterm krusader kcalc elisa
status=$?
echo
pacman -Q copyq kvantum rofi xterm krusader kcalc elisa 2>&1 | sed 's/^/  /'
pacman -Q vlc-plugin-ffmpeg vlc
[ $status -eq 0 ] && echo && echo "OK — removed; VLC keeps its plugin"
exit $status
