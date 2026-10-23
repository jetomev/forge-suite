#!/usr/bin/env bash
# Install the three locally built packages of 2026-10-22 through nog — alacrittyForge 1.1.1, bitlaForge 1.1.1
# (both now from the Forge Suite) and grubForge 2.2.2, each with its launcher entry — then check the entries
# landed and are valid. The maintainer runs it: nog asks for the password. Nothing comes from the AUR;
# the AUR push follows only after his test (the three test matrices in each app's testing/).
set -uo pipefail
P=~/Programs
LOGS=$P/forge-suite/logs
mkdir -p "$LOGS"
LOG="$LOGS/install-local-builds-$(date +%Y%m%d-%H%M%S).log"
ln -sf "$(basename "$LOG")" "$LOGS/install-local-builds-latest.log"
exec > >(tee "$LOG") 2>&1

echo
echo "── Forge Suite · the locally built packages of 2026-10-22 ──"
echo
pkgs=("$P/aur-alacrittyforge/alacrittyforge-1.1.1-1-any.pkg.tar.zst"
      "$P/aur-bitlaforge/bitlaforge-1.1.1-1-any.pkg.tar.zst"
      "$P/aur-grubforge/grubforge-2.2.2-1-any.pkg.tar.zst")
for p in "${pkgs[@]}"; do
  [ -f "$p" ] || { echo "  missing: $p — nothing was installed"; exit 1; }
done
nog install "${pkgs[@]}"
status=$?
echo
if [ $status -ne 0 ]; then
  echo "  nog stopped (status $status): nothing else was checked."
  exit $status
fi
pacman -Q alacrittyforge bitlaforge grubforge
echo
bad=0
for a in alacrittyforge bitlaforge grubforge; do
  f=/usr/share/applications/$a.desktop
  if [ -f "$f" ] && desktop-file-validate "$f" >/dev/null 2>&1 && [ -z "$(desktop-file-validate "$f")" ]; then
    echo "  $a: launcher entry installed and valid"
  else
    echo "  $a: launcher entry MISSING or not valid ($f)"; bad=1
  fi
  printf '  %s\n' "$($a --version 2>&1 | head -1)"
done
echo
[ $bad = 0 ] && echo "  OK — installed; now the test matrices (§2 in each app's testing/)." || echo "  Something is off: read the lines above."
echo "  Log: $LOG"
echo "  Done."
