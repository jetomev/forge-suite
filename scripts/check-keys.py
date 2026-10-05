#!/usr/bin/env python3
"""Compare the key chart (applets/help/keys.toml) with the keys Sway really has (sway/config).

Run by the git pre-commit hook (scripts/hooks/pre-commit): a key added, changed or removed in
one place and not the other stops the commit and says which. The chart can never quietly fall
out of date.

    python3 scripts/check-keys.py        exit 0 = they agree; 1 = the differences are printed
"""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "sway/config"
CHART = ROOT / "applets/help/keys.toml"
WORKSPACES = ROOT / "applets/workspaces/workspaces.toml"


def sway_keys():
    """Every bindsym in sway/config, as written ("$mod+Return"); resize mode as "resize:…"."""
    keys, mode = set(), None
    for line in CONFIG.read_text().splitlines():
        line = line.split("#", 1)[0].strip() if not line.strip().startswith("#") else ""
        if not line:
            continue
        m = re.match(r'mode\s+"([^"]+)"\s*\{', line)
        if m:
            mode = m.group(1)
            continue
        if line == "}" and mode:
            mode = None
            continue
        m = re.match(r"bindsym\s+((?:--\S+\s+)*)(\S+)", line)
        if m:
            keys.add(f"{mode}:{m.group(2)}" if mode else m.group(2))
    return keys


def applet_unbinds():
    """Workspace number keys that applet 1 switches off (beyond the configured workspaces)."""
    with open(WORKSPACES, "rb") as f:
        count = len(tomllib.load(f).get("workspace", []))
    keys = [str(i) for i in range(count + 1, 10)] + ["0"]
    return {f"$mod+{k}" for k in keys} | {f"$mod+Shift+{k}" for k in keys}


def chart_keys():
    with open(CHART, "rb") as f:
        chart = tomllib.load(f)
    return {k for g in chart.get("group", []) for e in g.get("keys", []) for k in e.get("sway", [])}


def main():
    real = sway_keys() - applet_unbinds()
    chart = chart_keys()
    missing = sorted(real - chart)   # in Sway, not explained in the chart
    stale = sorted(chart - real)     # in the chart, but Sway has no such key
    if not missing and not stale:
        print(f"check-keys: the key chart matches Sway ({len(real)} keys)")
        return 0
    print("check-keys: the key chart (applets/help/keys.toml) and sway/config disagree:")
    for k in missing:
        print(f"  in Sway but not in the chart:  {k}")
    for k in stale:
        print(f"  in the chart but not in Sway:  {k}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
