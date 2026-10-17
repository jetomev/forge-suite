#!/usr/bin/env bash
# Javier's test of the moved wallpaper generator (2026-10-17): the look command draws one wallpaper
# the way it does for a drawn style (mountains, in your current colour theme), through
# applets/theme/wallpaper-generate.py, into ~/Pictures/hypeforge-test/, then opens it in the image
# viewer. Your desktop, look and wallpaper are not touched.
#
#   bash ~/Programs/forge-suite/hypeforge/scripts/test-wallpaper-generator.sh
#
# Logs to logs/test-wallpaper-generator-<time>.log (+ -latest); the last line says OK.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/test-wallpaper-generator-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/test-wallpaper-generator-latest.log
exec > >(tee "$log") 2>&1
out_dir="$HOME/Pictures/hypeforge-test"
python3 - "$out_dir" <<'PY'
import importlib.machinery, importlib.util, sys, time, tomllib
from pathlib import Path
loader = importlib.machinery.SourceFileLoader("ht", "applets/theme/hypeforge-theme")
spec = importlib.util.spec_from_loader("ht", loader); m = importlib.util.module_from_spec(spec); loader.exec_module(m)
look = tomllib.loads((Path.home() / ".config/hypeforge/look.toml").read_text())
slug = look.get("colors", "kognogos-mocha")
t = tomllib.loads(m.COLOURS.read_text())["themes"][slug]
print(f"generator: {m.WALLGEN}")
print(f"colours:   {slug}")
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for old in out.glob("mountains-*.png"):
    old.unlink()
t0 = time.time()
pic = m.topic_wallpaper("mountains", slug, t, out)
from PIL import Image
print(f"drew:      {pic}  {Image.open(pic).size[0]}x{Image.open(pic).size[1]}  in {time.time() - t0:.1f} s")
print(pic, file=open(out / "last.txt", "w"))
PY
pic="$(cat "$out_dir/last.txt")"
xdg-open "$pic" >/dev/null 2>&1 &
echo "OK: the picture is open in your image viewer"
