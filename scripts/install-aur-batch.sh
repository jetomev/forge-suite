#!/usr/bin/env bash
# Javier's local test of the 2026-10-11 dependency-audit batch (forge-suite#91): install the six packages
# built from the AUR recipes (makepkg, signed sources, tests passed), through nog, then show what's installed.
# The AUR pushes come only after this passes (our rule: the AUR push is the last step, never a test step).
#
#   bash ~/Programs/forge-suite/scripts/install-aur-batch.sh
#
# nog asks for the password once. Writes logs/install-aur-batch-<time>.log and logs/install-aur-batch-latest.log.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
LOGS="$HERE/logs"; mkdir -p "$LOGS"
LOG="$LOGS/install-aur-batch-$(date +%Y%m%d-%H%M%S).log"
ln -sf "$(basename "$LOG")" "$LOGS/install-aur-batch-latest.log"
exec > >(tee "$LOG") 2>&1

P=~/Programs
pkgs=(
  "$P/aur-nog/nog-1.8.0-2-x86_64.pkg.tar.zst"
  "$P/aur-workspaceforge/workspaceforge-1.0.0-2-any.pkg.tar.zst"
  "$P/aur-nogforge/nogforge-1.4.0-2-any.pkg.tar.zst"
  "$P/aur-displayforge/displayforge-1.1.1-1-any.pkg.tar.zst"
  "$P/aur-nightforge/nightforge-1.1.0-1-any.pkg.tar.zst"
  "$P/aur-grubforge/grubforge-2.2.1-1-any.pkg.tar.zst"
)

echo
echo "==> The dependency-audit batch: six packages, installed through nog"
echo
for p in "${pkgs[@]}"; do
  [ -f "$p" ] || { echo "Missing: $p (build it first)"; exit 1; }
  echo "    $(basename "$p")"
done
echo
nog install "${pkgs[@]}"

echo
echo "==> What's installed now"
pacman -Q nog workspaceforge nogforge displayforge nightforge grubforge
echo
echo "==> What each one now depends on (the new needs: sudo + zstd, python-rich, glib2, grub)"
for n in nog workspaceforge nogforge displayforge nightforge grubforge; do
  printf '    %-15s %s\n' "$n" "$(pacman -Qi "$n" | sed -n 's/^Depends On *: //p')"
done
echo
echo "OK — now open displayForge, nightForge, grubForge, workspaceForge and nogForge once each,"
echo "     and check the night light's tray icon on the Rice (none) and on Windows 11 (shown)."
echo "     Thanks! The AUR pushes follow your OK."
