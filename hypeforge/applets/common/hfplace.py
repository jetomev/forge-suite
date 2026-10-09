"""hypeForge applets · Window Placement's fill order (D-47, D-50), shared.

Window Placement uses it for every new window; the Workspaces applet uses it for a window it has
just taken to its own workspace (F-50, #55), so that window lands in the next free spot too.
Python standard library only.
"""

import os
import tomllib
from pathlib import Path

from hfapps import taken_over
from hfsway import GET_TREE, GET_WORKSPACES, quoted

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "hypeforge/applets/placement.toml"
SPOTS = ["fill", "right", "under-right"]  # the order spots come in on one screen
MARK = "_hypeforge_place"


def load():
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    order = [(int(o["screen"]) - 1, o["spot"]) for o in cfg.get("order", []) if o.get("spot") in SPOTS]
    return bool(cfg.get("enabled", False)), list(cfg.get("screens", [])), order


# ---- Reading Sway's tree ---------------------------------------------------------------------

def find(node, test):
    if test(node):
        return node
    for child in node.get("nodes", []) + node.get("floating_nodes", []):
        hit = find(child, test)
        if hit:
            return hit
    return None


def leaves(node, skip=None):
    """The tiled windows inside `node`, left to right / top to bottom (floating ones not)."""
    if not node.get("nodes") and node.get("type") == "con":
        return [] if node["id"] == skip else [node]
    return [w for child in node.get("nodes", []) for w in leaves(child, skip)]


def top(workspace, skip):
    """The workspace's main pieces: [left, right] — skipping wrappers with a single child."""
    node = workspace
    while True:
        kids = [k for k in node.get("nodes", []) if leaves(k, skip)]
        if len(kids) == 1 and kids[0].get("nodes"):
            node = kids[0]
            continue
        return kids


def spot_container(workspace, spot, skip):
    """The container that holds `spot` on this workspace now, or None."""
    kids = top(workspace, skip)
    if spot == "fill":
        return kids[0] if kids else None
    if len(kids) < 2:
        return None
    right = kids[1]
    column = [k for k in right.get("nodes", []) if leaves(k, skip)] if right.get("layout") == "splitv" else []
    if spot == "right":
        return column[0] if column else right
    return column[1] if len(column) > 1 else None  # under-right


# ---- Placing ---------------------------------------------------------------------------------

def place(sway, screens, order, new_id, handed_over=False):
    """Put window `new_id` in the next free spot. `handed_over`: the Workspaces applet calls this
    for a window it has taken to its workspace; Placement's own watcher leaves those alone."""
    tree = sway.ask(GET_TREE)
    new = find(tree, lambda n: n.get("id") == new_id)
    if not new or new.get("type") != "con":  # floating windows are "floating_con"
        return
    if taken_over(new) and not handed_over:  # the Workspaces applet is placing it (F-50)
        return
    shown = {ws["output"]: ws["name"] for ws in sway.ask(GET_WORKSPACES) if ws["visible"]}
    workspaces = [find(tree, lambda n, name=shown.get(s): n.get("type") == "workspace" and n.get("name") == name)
                  for s in screens]
    home = find(tree, lambda n: n.get("type") == "workspace" and find(n, lambda m: m.get("id") == new_id))
    if not home or home["name"] not in [w["name"] for w in workspaces if w]:
        return  # it opened somewhere not on screen (sent there on purpose): leave it

    counts = [len(leaves(w, new_id)) if w else 0 for w in workspaces]
    # The next free spot: the first in the order whose screen has exactly the spots before it.
    for screen, spot in order:
        if screen < len(workspaces) and workspaces[screen] and counts[screen] == SPOTS.index(spot):
            return put(sway, workspaces[screen], screen, spot, new_id, tab=False)
    # Every spot taken: round the order again, as tabs.
    total = sum(counts)
    screen, spot = order[(total - len(order)) % len(order)] if total >= len(order) else order[0]
    if screen < len(workspaces) and workspaces[screen]:
        put(sway, workspaces[screen], screen, spot, new_id, tab=True)


def put(sway, workspace, screen, spot, new_id, tab):
    me = f"[con_id={new_id}]"
    if not tab and spot == "fill":
        sway.run(f"{me} move container to workspace {quoted(workspace['name'])}", f"{me} focus")
        return
    if tab:
        target = spot_container(workspace, spot, new_id)
        if not target:
            return
        if target.get("layout") in ("tabbed", "stacked") and target.get("nodes"):
            anchor = target["nodes"][-1]["id"]          # join the tabs, as the last one
            prepare = []
        else:
            anchor = (leaves(target, new_id) or [target])[0]["id"]
            prepare = [f"[con_id={anchor}] split v", f"[con_id={anchor}] layout tabbed"]
    else:
        windows = leaves(workspace, new_id)
        if spot == "right":
            anchor, prepare = windows[0]["id"], [f"[con_id={windows[0]['id']}] split h"]
        else:  # under-right: below the right-hand window
            anchor, prepare = windows[-1]["id"], [f"[con_id={windows[-1]['id']}] split v"]
    sway.run(*prepare,
             f"[con_id={anchor}] mark --add {MARK}",
             f"{me} move container to mark {MARK}",
             f"[con_id={anchor}] unmark {MARK}",
             f"{me} focus")
