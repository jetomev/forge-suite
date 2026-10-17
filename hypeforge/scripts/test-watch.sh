#!/usr/bin/env bash
# Javier's test of #54 (2026-10-17): a pretend applet that crashes on purpose, run through the
# watcher exactly as Sway runs the real ones. A notification should appear on your screen at once and
# stay until you click it. Nothing real is stopped or changed.
#
#   bash ~/Programs/forge-suite/hypeforge/scripts/test-watch.sh
#
# Logs to logs/test-watch-<time>.log (+ -latest); the last line says OK.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/test-watch-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/test-watch-latest.log
exec > >(tee "$log") 2>&1
echo "a pretend applet called test-crash starts, then crashes on purpose…"
status=0
applets/common/hypeforge-watch test-crash python3 -c "raise RuntimeError('this crash is on purpose (the #54 test)')" || status=$?
echo "the watcher ended with status $status (1 = it saw the crash)"
echo "the pretend applet's log:"
sed 's/^/    /' ~/.local/state/hypeforge/logs/test-crash.log | tail -8
[ "$status" -eq 1 ] && echo "OK: now look at your screen, top right"
