#!/bin/sh
# Build the plan page: the shared page styling from review 7 + this page's body.
cd "$(dirname "$0")" && python3 - <<'PY'
from pathlib import Path
t = Path("../review-7-cosmic/template.html").read_text()
head = t[:t.index("/* ── the screen")].replace("<title>hypeForge Look Review 7</title>", "<title>hypeForge Look Build Plan</title>")
Path("index.html").write_text(head + Path("template-body.html").read_text())
PY
