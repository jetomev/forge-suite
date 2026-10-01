#!/usr/bin/env bash
# hypeForge on this computer, step 2 of 4: install the desktop's programs through nog.
# Plasma is not touched; it stays as the other choice at the login screen (D-6).
# Everything printed is saved to logs/this-pc-install-latest.log; when it ends,
# just say "done" (the last line says FINISHED OK, or the log stops at the error).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$REPO/logs"
LOG="$REPO/logs/this-pc-install-$(date +%Y%m%d-%H%M).log"
ln -sfn "$(basename "$LOG")" "$REPO/logs/this-pc-install-latest.log"

# From Arch's official repositories (29). Noctalia is the desktop shell (D-40).
repo=(
  hyprland uwsm xdg-desktop-portal-hyprland hyprpolkitagent
  hyprlock hypridle hyprsunset hyprpicker noctalia
  grim slurp satty wl-clipboard playerctl adw-gtk-theme qt6-wayland
  superfile krusader thunar-volman thunar-archive-plugin tumbler udiskie gvfs
  imv zathura zathura-pdf-mupdf mpv mpv-mpris nvtop
)
# From the AUR (3), after Hyprland: the title bars are built against it.
aur=(hyprland-plugin-hyprbars monique cliamp)

{
  echo "== 1 of 2 · ${#repo[@]} packages from the official repositories"
  nog install "${repo[@]}"
  echo "== 2 of 2 · ${#aur[@]} packages from the AUR"
  nog install "${aur[@]}"
  missing=0
  for p in "${repo[@]}" "${aur[@]}"; do
    pacman -Q "$p" >/dev/null 2>&1 || { echo "MISSING: $p"; missing=1; }
  done
  [ "$missing" -eq 0 ] && echo "== FINISHED OK: all $(( ${#repo[@]} + ${#aur[@]} )) installed"
} 2>&1 | tee "$LOG"
