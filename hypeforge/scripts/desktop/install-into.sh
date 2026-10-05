#!/usr/bin/env bash
# install-into.sh — put the hypeForge desktop into one home folder.
#
#   bash scripts/desktop/install-into.sh <home-folder>
#
# Used by KognogOS's ISO build (for /etc/skel and the live user) and by its
# installer; later by the hypeForge app itself. It only writes inside the
# folder it is given. Nothing is installed; the packages come from nog.
#
# What it does:
#   1. copies desktop/ to <home>/.config/hypeforge/ (the one portable folder, D-8, D-28)
#   2. points ~/.config/{hypr,uwsm,noctalia} into it; anything already
#      there is moved aside to <name>.before-hypeforge, never deleted
#   3. links the background helpers as systemd user services and switches them on (D-25)
#   4. writes the default theme's colour files (Catppuccin Mocha, D-36), so the very
#      first login already has them
set -euo pipefail

SRC="$(cd "$(dirname "$0")/../../desktop" && pwd)"
H="${1:?usage: install-into.sh <home-folder>}"
[[ -d "$H" ]] || { echo "!! no such folder: $H" >&2; exit 1; }
CFG="$H/.config"
HF="$CFG/hypeforge"

mkdir -p "$CFG"
rm -rf "$HF"
cp -r "$SRC" "$HF"
echo "==> $HF"

for d in hypr uwsm noctalia; do
    t="$CFG/$d"
    if [[ -e "$t" || -L "$t" ]] && [[ "$(readlink "$t")" != "hypeforge/$d" ]]; then
        mv "$t" "$t.before-hypeforge"
        echo "    kept the old $d as $d.before-hypeforge"
    fi
    ln -sfn "hypeforge/$d" "$t"
done

# hypeForge's own menu entries (the shortcut list, F-9).
A="$H/.local/share/applications"
mkdir -p "$A"
for f in "$HF"/applications/*.desktop; do
    ln -sfn "../../../.config/hypeforge/applications/$(basename "$f")" "$A/$(basename "$f")"
done

# Autostart entries hypeForge switches off (Hidden=true copies, D-25).
mkdir -p "$CFG/autostart"
for f in "$HF"/autostart/*.desktop; do
    ln -sfn "../hypeforge/autostart/$(basename "$f")" "$CFG/autostart/$(basename "$f")"
done

U="$CFG/systemd/user"
mkdir -p "$U/graphical-session.target.wants"
for f in "$HF"/systemd/*.service; do
    n="$(basename "$f")"
    ln -sfn "../../hypeforge/systemd/$n" "$U/$n"
    ln -sfn "../$n" "$U/graphical-session.target.wants/$n"
done
echo "    $(ls "$HF"/systemd/*.service | wc -l) background helpers switched on"

# The colour files: run theme.lua once with a stand-in for Hyprland.
mkdir -p "$CFG/alacritty/themes"
HOME="$H" lua - <<'LUA'
hl = { dsp = { exec_cmd = function(c) return c end }, dispatch = function() end,
       config = function() end, bind = function() end, unbind = function() end }
dofile(os.getenv("HOME") .. "/.config/hypeforge/hypr/theme.lua")
print("    theme files written: " .. HYPEFORGE_THEME.name)
LUA
