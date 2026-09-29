#!/usr/bin/env bash
# The short version of TODO.md. Printed at session start by a hook, and after every step.
# There is no second copy of the truth here -- it reads TODO.md and counts.
cd "$(dirname "$0")/.." || exit 1
python3 - "$@" <<'PY'
import re, pathlib, subprocess, sys

t = pathlib.Path("TODO.md").read_text().splitlines()
phases, cur, locked_open = [], None, []
for ln in t:
    # A "Track" runs alongside the phases and counts toward the total.
    m = re.match(r"^## ((?:Phase \d+|Track) · [^—]+?)(\s+—\s+\*\*(.+)\*\*)?$", ln.strip())
    if m:
        cur = {"name": m.group(1).strip(), "note": m.group(3) or "", "done": 0, "open": [], }
        phases.append(cur); continue
    if ln.startswith("## "):
        cur = None
        if "Javier's hands" in ln: cur = {"name": "JAVIER", "done": 0, "open": [], "note": ""}; phases.append(cur)
        elif "Open questions" in ln: cur = {"name": "QUESTIONS", "done": 0, "open": [], "note": ""}; phases.append(cur)
        continue
    if cur is None: continue
    if ln.startswith("- [x]"): cur["done"] += 1
    elif ln.startswith("- [ ]"):
        item = re.sub(r"\*\*|`", "", ln[5:].strip())
        cur["open"].append(item)

work = [p for p in phases if p["name"].startswith(("Phase", "Track"))]
tot_d = sum(p["done"] for p in work); tot_o = sum(len(p["open"]) for p in work)
pct = round(100 * tot_d / (tot_d + tot_o)) if (tot_d + tot_o) else 0

try:
    head = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
except Exception:
    head, dirty = "", ""

print("\n╭─ hypeForge · Forge Suite · the KognogOS Hyprland desktop")
# The target is read from TODO.md's own **Target:** line, so there is only one copy of it.
tgt = next((m.group(1).rstrip(".") for ln in t for m in [re.match(r"^\*\*Target:\s*(.+?)\*\*", ln)] if m),
           "(no **Target:** line in TODO.md)")
print(f"│  target {tgt} · {tot_d}/{tot_d+tot_o} steps done · {pct}%")
print(f"│  {head}" + ("  ⚠ uncommitted changes" if dirty else "  ✓ clean"))
print("╰─" + "─" * 60)

for p in work:
    n = len(p["open"]); d = p["done"]
    state = "✅" if n == 0 and d else ("🔄" if d else "⬜")
    print(f"  {state} {p['name']:<42} {d}/{d+n}")

active = next((p for p in work if p["open"] and p["name"].startswith("Phase")), None)
if active:
    print(f"\n  NEXT — {active['name']}")
    for i in active["open"][:5]:
        print(f"    □ {i[:88]}")
    if len(active["open"]) > 5:
        print(f"    … {len(active['open'])-5} more in this phase")

for p in work:
    if p["name"].startswith("Track") and p["open"]:
        print(f"\n  ALONGSIDE — {p['name']}")
        for i in p["open"][:3]:
            print(f"    □ {i[:88]}")
        if len(p["open"]) > 3:
            print(f"    … {len(p['open'])-3} more on this track")

for key, label in (("JAVIER", "WAITING ON JAVIER"), ("QUESTIONS", "OPEN QUESTIONS")):
    blk = next((p for p in phases if p["name"] == key), None)
    if blk and blk["open"]:
        print(f"\n  {label}")
        for i in blk["open"][:6]:
            print(f"    □ {i[:88]}")
print()
PY
