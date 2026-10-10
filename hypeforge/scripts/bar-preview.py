#!/usr/bin/env python3
"""See a bar part before it reaches the desktop (look program step 3, the bar parts).

Starts a screen-less Sway (one fake 2560×1440 screen, its own runtime and config folders), runs
the Workspaces applet from this repository against it, writes the chosen style + theme with
hypeforge-theme into the bench's folder, opens a few windows so some workspaces are busy, runs
Waybar with a small test layout and photographs the top of the screen. Nothing touches the real
desktop: not its Sway, its bar, its applets or its settings.

    bar-preview.py [--part pills|taskbar] [--theme kognogos-mocha] [--style rice] [--out picture.png]

Writes the picture (default: logs/bar-preview-<style>-<theme>.png) and prints where it is.
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APPLETS = HERE / "applets"
SCREEN = "HEADLESS-1"

WORKSPACES_TOML = f'''enabled = true
screens = ["{SCREEN}"]
[[workspace]]
name = "Daily"
[[workspace]]
name = "Work"
[[workspace]]
name = "Entertainment"
[[workspace]]
name = "Gaming"
[[workspace]]
name = "Monitoring"
[[workspace]]
name = "Settings"
'''

# A test layout with the parts step 3 builds; each style's real layout comes in step 5.
BAR = {
    "layer": "top", "position": "top", "height": 38, "spacing": 0,
    "include": ["{fragment}"],
    "modules-left": ["custom/emblem", "group/workspace-pills"],
    "modules-center": ["clock"],
    "modules-right": ["cpu", "memory"],
    "custom/emblem": {"format": "  ", "tooltip": False},
    "clock": {"format": "{:%a %d %b   %I:%M %p}"},
    "cpu": {"format": "  {usage}%"},
    "memory": {"format": "  {percentage}%"},
}

# The taskbar part's test layout: the row in the centre, its icons' stylesheet imported
TASKBAR = {
    "layer": "top", "position": "top", "height": 48, "spacing": 0,
    "include": ["{fragment}"],
    "modules-center": ["group/taskbar"],
}
TASKBAR_CSS = '''@import url("file://{colors}");
@import url("file://{icons}");
* {{ font-size: 13px; min-height: 0; }}
window#waybar {{ background: transparent; color: @hf_text; }}
.modules-center {{ background: @hf_bar; border-radius: 10px; margin: 6px 0 0 0; padding: 0 6px; }}
/* the taskbar row (look step 3): one icon per app; a line under running apps, a longer one on the app in use */
.app {{ min-width: 40px; margin: 4px 2px; padding: 0; border-radius: 6px; }}
.app.running {{ box-shadow: inset 0 -2px @hf_task_running; }}
.app.focused {{ box-shadow: inset 0 -3px @hf_task_focused; background-color: @hf_pill_hover; }}
.app.urgent {{ box-shadow: inset 0 -3px @hf_alert; }}
.app:hover {{ background-color: @hf_pill_hover; }}
'''

# The Mac menus' test layout (Mac OS 9, D-72): the platinum menu bar, its drop-down menus
MENUBAR = {
    "layer": "top", "position": "top", "height": 24, "spacing": 0,
    "include": ["{fragment}"],
    "modules-left": ["group/menubar"],
    "modules-right": ["clock", "custom/menu-appicon"],
    "clock": {"format": "{:%I:%M %p}"},
}
MENUBAR_CSS = '''@import url("file://{colors}");
@import url("file://{icons}");
* {{ font-family: "Noto Sans", sans-serif; font-size: 13px; font-weight: bold; min-height: 0; }}
window#waybar {{ background: @hf_menubar_bg; color: @hf_menubar_text; border-bottom: 1px solid @hf_menubar_line; }}
#custom-menu-emblem {{ background-image: url("file://{emblem}"); background-size: 17px 17px; background-repeat: no-repeat;
                       background-position: center; min-width: 30px; }}
#custom-menu-app, #custom-menu-window, #custom-menu-special, #custom-menu-help, #clock {{ padding: 0 10px; }}
#custom-menu-emblem:hover, #custom-menu-window:hover, #custom-menu-special:hover, #custom-menu-help:hover {{
    background-color: @hf_menu_hl; color: @hf_menu_hl_text; }}
#custom-menu-appicon {{ min-width: 30px; margin-right: 4px; }}
.app {{ background-size: 18px 18px; }}
menu {{ background: @hf_menu_bg; color: @hf_menubar_text; border: 1px solid @hf_menubar_line; padding: 2px 0; border-radius: 0; }}
menuitem {{ padding: 3px 18px; font-weight: normal; }}
menuitem:hover {{ background: @hf_menu_hl; color: @hf_menu_hl_text; }}
'''

# The pager part's test layout (KDE's K-2): a box per workspace, dots for its windows
PAGER = {
    "layer": "top", "position": "top", "height": 44, "spacing": 0,
    "include": ["{fragment}"],
    "modules-left": ["group/pager"],
}
PAGER_CSS = '''@import url("file://{colors}");
* {{ font-family: "Noto Sans", sans-serif; min-height: 0; }}
window#waybar {{ background: transparent; }}
.modules-left {{ background: @hf_bar; border-radius: 8px; margin: 6px 10px 0; padding: 0 6px; }}
.pager {{ border: 1px solid @hf_pager_border; border-radius: 3px; min-width: 40px; margin: 6px 2px; padding: 0 4px;
          color: @hf_pager_window; font-size: 7px; }}
.pager.active {{ background: @hf_pager_active; }}
.pager:hover {{ border-color: @hf_pager_window; }}
'''

CSS = '''@import url("file://{colors}");
* {{ font-family: "JetBrainsMono Nerd Font", monospace; font-size: 13px; min-height: 0; }}
window#waybar {{ background: transparent; color: @hf_text; }}
.modules-left, .modules-center, .modules-right {{
    background: @hf_bar; border-radius: 10px; margin: 8px 10px 0 10px; padding: 0 6px; }}
#custom-emblem {{ color: @hf_new; padding: 0 8px 0 6px; }}
#clock, #cpu, #memory {{ padding: 0 10px; }}
/* the workspace pills (look step 3): numbers; the active one wide, with its name */
.pill {{ border-radius: 999px; padding: 0 8px; margin: 6px 2px; min-width: 14px; color: @hf_pill_empty; }}
.pill.busy {{ color: @hf_pill_busy; box-shadow: inset 0 -2px @hf_pill_busy; border-radius: 0; margin: 6px 6px; padding: 0 2px; }}
.pill.active {{ background: @hf_pill_active; color: @hf_pill_active_text; padding: 0 14px; font-weight: bold; }}
.pill:hover {{ background: @hf_pill_hover; }}
'''


class IPC:
    def __init__(self, path):
        self.s = socket.socket(socket.AF_UNIX)
        self.s.connect(path)

    def ask(self, kind, payload=""):
        data = payload.encode()
        self.s.sendall(b"i3-ipc" + struct.pack("=II", len(data), kind) + data)
        head = self.s.recv(14, socket.MSG_WAITALL)
        size, _ = struct.unpack("=II", head[6:])
        return json.loads(self.s.recv(size, socket.MSG_WAITALL))


def load_theme_tool():
    loader = importlib.machinery.SourceFileLoader("hypeforge_theme", str(APPLETS / "theme/hypeforge-theme"))
    spec = importlib.util.spec_from_loader("hypeforge_theme", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--part", default="pills", choices=["pills", "taskbar", "pager", "menubar"])
    ap.add_argument("--theme", default="kognogos-mocha")
    ap.add_argument("--style", default="rice")
    ap.add_argument("--switch", type=int, default=4, help="the workspace on screen in the picture")
    ap.add_argument("--out")
    ap.add_argument("--open", type=int, nargs=1, help="menubar: click at this x to open a menu in the picture")
    a = ap.parse_args()
    out = Path(a.out or HERE / f"logs/bar-preview-{a.part}-{a.style}-{a.theme}.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    base = Path(tempfile.mkdtemp(prefix="hfbar.", dir="/tmp"))   # short: the IPC socket path must fit
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(WORKSPACES_TOML)
    ht = load_theme_tool()
    ht.apply(a.style, a.theme, ht.Place(conf), wallpaper=None, reload=False, check_names=False,
             make_wallpaper=False, say=lambda *_: None)
    colors = conf / "hypeforge/theme/colors.css"
    if a.part == "menubar":
        real = Path.home() / ".config/hypeforge/applets/sections.toml"   # the real groups, read only
        (conf / "hypeforge/applets/sections.toml").write_text(real.read_text())
        fragment = conf / "hypeforge/applets/menubar.waybar.json"
        (base / "bar.json").write_text(json.dumps(MENUBAR).replace("{fragment}", str(fragment)))
        (base / "bar.css").write_text(MENUBAR_CSS.format(colors=colors, icons=conf / "hypeforge/applets/menubar.css",
                                                         emblem=HERE / "assets/kognogos-emblem.png"))
    elif a.part == "taskbar":
        (conf / "hypeforge/applets/sections.toml").write_text(
            'favourites = ["Alacritty", "thunar", "google-chrome", "com.anthropic.Claude", "steam", "spotify", "discord"]\n')
        fragment = conf / "hypeforge/applets/taskbar.waybar.json"
        (base / "bar.json").write_text(json.dumps(TASKBAR).replace("{fragment}", str(fragment)))
        (base / "bar.css").write_text(TASKBAR_CSS.format(colors=colors, icons=conf / "hypeforge/applets/taskbar.css"))
    else:
        fragment = conf / "hypeforge/applets/workspaces.waybar.json"
        layout, css = (PAGER, PAGER_CSS) if a.part == "pager" else (BAR, CSS)
        (base / "bar.json").write_text(json.dumps(layout).replace("{fragment}", str(fragment)))
        (base / "bar.css").write_text(css.format(colors=colors))
    wall = ht.token(ht.themes()[a.theme], "surface.sunken")
    (base / "sway.conf").write_text(f"output {SCREEN} resolution 2560x1440 bg {wall} solid_color\n"
                                    "xwayland disable\ndefault_border pixel 2\ngaps inner 10\n")
    fakebin = base / "bin"
    fakebin.mkdir()
    (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
    (fakebin / "pgrep").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless",
               WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1",
               PATH=f"{fakebin}:{os.environ['PATH']}")
    procs, log = [], open(base / "preview.log", "w")
    try:
        procs.append(subprocess.Popen(["sway", "--unsupported-gpu", "-c", str(base / "sway.conf")],
                                      env=env, stdout=log, stderr=log))
        sock = None
        for _ in range(100):
            found = list(run.glob("sway-ipc.*.sock"))
            if found:
                sock = str(found[0]); break
            time.sleep(0.1)
        if not sock:
            print("the preview's Sway did not start; see", base / "preview.log"); return 1
        env["SWAYSOCK"] = sock
        env["WAYLAND_DISPLAY"] = next((p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock")), "wayland-1")
        ipc = IPC(sock)
        procs.append(subprocess.Popen([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces")],
                                      env=env, stdout=log, stderr=log))
        time.sleep(1.5)
        # busy workspaces: a window on 1 and on 3 (an X-less GTK window, as the bench does)
        window = ("import gi, sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
                  "GLib.set_prgname(sys.argv[1]); w=Gtk.Window(); w.show_all(); "
                  "GLib.timeout_add_seconds(60, Gtk.main_quit); Gtk.main()")
        if a.part == "menubar":
            procs.append(subprocess.Popen([sys.executable, str(APPLETS / "menubar/hypeforge-menubar")],
                                          env=env, stdout=log, stderr=log))
            procs.append(subprocess.Popen([sys.executable, "-c", window, "google-chrome"],
                                          env={**env, "GDK_BACKEND": "wayland"}, stdout=log, stderr=log))
            time.sleep(1.5)
        if a.part == "taskbar":
            procs.append(subprocess.Popen([sys.executable, str(APPLETS / "taskbar/hypeforge-taskbar")],
                                          env=env, stdout=log, stderr=log))
            # stand-ins named like real apps: Chrome and Thunar are pinned, GIMP is not; Chrome twice
            for name in ("thunar", "gimp", "google-chrome", "google-chrome"):
                procs.append(subprocess.Popen([sys.executable, "-c", window, name], env={**env, "GDK_BACKEND": "wayland"},
                                              stdout=log, stderr=log))
                time.sleep(1.0)
        for ws in {"pills": (1, 3), "pager": (1, 1, 1, 3, 3, 5)}.get(a.part, ()):
            subprocess.run([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces"), "go", str(ws)], env=env)
            procs.append(subprocess.Popen([sys.executable, "-c", window, "bench"], env={**env, "GDK_BACKEND": "wayland"},
                                          stdout=log, stderr=log))
            time.sleep(1.2)
        if a.part in ("pills", "pager"):
            subprocess.run([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces"), "go", str(a.switch)], env=env)
        procs.append(subprocess.Popen(["waybar", "-c", str(base / "bar.json"), "-s", str(base / "bar.css")],
                                      env=env, stdout=log, stderr=log))
        time.sleep(3)
        region = "0,0 2560x56"
        if a.part == "menubar" and a.open:   # click a menu open (the hidden seat's pointer), then a submenu
            ipc.ask(0, f"seat seat0 cursor set {a.open[0]} 12")
            ipc.ask(0, "seat seat0 cursor press button1")
            ipc.ask(0, "seat seat0 cursor release button1")
            time.sleep(1.5)
            region = "0,0 1100x620"
        shot = base / "shot.png"
        subprocess.run(["grim", "-g", region, str(shot)], env=env, check=True)
        out.write_bytes(shot.read_bytes())
        print(out)
        return 0
    finally:
        try:
            IPC(sock).ask(0, "exit") if sock else None
        except Exception:
            pass
        for p in reversed(procs):
            p.terminate()
        for p in procs:
            try:
                p.wait(5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    sys.exit(main())
