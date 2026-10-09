#!/usr/bin/env bash
# Install the locally built packages of the 2026-10-08 release through nog (alacrittyForge 1.1.0,
# nogForge 1.4.0, grubForge 2.2.0, bitlaForge 1.1.0; forgekit 0.10.0 went in first), then move the
# live hypeForge Settings page list to the new one (forge = true, "Boot Menu"), with a backup.
# Javier runs it: nog asks for the password. Nothing comes from the AUR.
set -uo pipefail
P=~/Programs
LOGS=$P/forge-suite/hypeforge/logs
mkdir -p "$LOGS"
LOG="$LOGS/install-local-builds-$(date +%Y%m%d-%H%M%S).log"
ln -sf "$(basename "$LOG")" "$LOGS/install-local-builds-latest.log"
exec > >(tee "$LOG") 2>&1

echo "Installing the locally built Forge apps ($(date '+%Y-%m-%d %H:%M'))"
echo
nog install \
  "$P/aur-alacrittyforge/alacrittyforge-1.1.0-1-any.pkg.tar.zst" \
  "$P/aur-nogforge/nogforge-1.4.0-1-any.pkg.tar.zst" \
  "$P/aur-grubforge/grubforge-2.2.0-1-any.pkg.tar.zst" \
  "$P/aur-bitlaforge/bitlaforge-1.1.0-1-any.pkg.tar.zst"
status=$?
echo
if [ $status -ne 0 ]; then
  echo "nog stopped (status $status): nothing else was changed."
  exit $status
fi
pacman -Q python-forgekit alacrittyforge nogforge grubforge bitlaforge
echo
LIVE=~/.config/hypeforge/applets/settings.toml
cp "$LIVE" "$LIVE.bak-$(date +%Y%m%d-%H%M%S)"
cp "$P/forge-suite/hypeforge/applets/settings/settings.toml" "$LIVE"
echo "Settings' page list updated (backup next to it)."
echo
echo "OK — installed; Settings starts the apps with --hypeforge"
