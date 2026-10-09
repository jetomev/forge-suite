#!/usr/bin/env python3
"""F-50 (#55) · one time: start each workspace's app list from the launcher's groups.

Until 2026-10-09 the launcher decided where an app opened: each group had a workspace (Games → 4)
and a few apps had their own (`[workspaces]` in sections.toml). From F-50 on, each workspace lists
its apps in workspaces.toml and that is the only place it is set (workspaceForge D-5, answer 7:
"the lists start from the launcher's groups, once"). This script does that once: it reads the
launcher's settings as they were, sorts every installed app into its group the launcher's own way,
and writes `apps = [...]` under each workspace's name.

    seed-workspace-apps.py SECTIONS WORKSPACES            show the lists, change nothing
    seed-workspace-apps.py SECTIONS WORKSPACES --write    write them (a backup first)

It refuses if any workspace already has a list: it starts lists, it never overwrites them.
"""

import importlib.machinery
import importlib.util
import re
import shutil
import sys
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LAUNCHER = HERE / "applets/sections/hypeforge-sections"
sys.path.insert(0, str(HERE / "applets/common"))
from hfapps import apps  # noqa: E402


def launcher():
    loader = importlib.machinery.SourceFileLoader("hfsections", str(LAUNCHER))
    spec = importlib.util.spec_from_loader("hfsections", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def seed(sections_path, workspaces_path):
    """{workspace number: [desktop ids]} the way the launcher placed them, and the names."""
    with open(sections_path, "rb") as f:
        cfg = tomllib.load(f)
    with open(workspaces_path, "rb") as f:
        ws = tomllib.load(f)
    names = [w["name"] for w in ws.get("workspace", [])]
    if any("apps" in w for w in ws.get("workspace", [])):
        sys.exit(f"{workspaces_path}: a workspace already has a list of apps; nothing changed")
    everything = apps()
    own = cfg.get("workspaces", {})
    lists = {i: [] for i in range(1, len(names) + 1)}
    for section, members in launcher().sort_into_sections(cfg, everything):
        for app_id in members:
            n = own.get(app_id, section.get("workspace"))
            if isinstance(n, int) and n in lists:
                lists[n].append(app_id)
    return names, {i: sorted(a, key=lambda x: everything[x]["name"].lower()) for i, a in lists.items()}


def write(workspaces_path, names, lists):
    text = Path(workspaces_path).read_text()
    out, block, i = [], False, 0
    for line in text.splitlines(keepends=True):
        out.append(line)
        if line.strip() == "[[workspace]]":
            block, i = True, i + 1
            continue
        if block and re.match(r'\s*name\s*=', line):
            items = ",\n".join(f"  {a!r}".replace("'", '"') for a in lists.get(i, []))
            out.append(f"apps = [\n{items},\n]\n" if items else "apps = []\n")
            block = False
    backup = Path(f"{workspaces_path}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(workspaces_path, backup)
    Path(workspaces_path).write_text("".join(out))
    with open(workspaces_path, "rb") as f:  # it must still read back, with the same lists
        back = tomllib.load(f)
    got = {n: w.get("apps", []) for n, w in enumerate(back["workspace"], 1)}
    if got != {n: lists.get(n, []) for n in got}:
        shutil.copy2(backup, workspaces_path)
        sys.exit("the written file did not read back the same: put back as it was")
    return backup


def main():
    args = [a for a in sys.argv[1:] if a != "--write"]
    if len(args) != 2:
        sys.exit(__doc__)
    names, lists = seed(*args)
    for i, n in enumerate(names, 1):
        print(f"{i}. {n}: {len(lists[i])} apps — {', '.join(lists[i]) or '(none)'}")
    if "--write" in sys.argv:
        print("backup:", write(args[1], names, lists))
        print("written:", args[1])


if __name__ == "__main__":
    main()
