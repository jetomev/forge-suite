#!/usr/bin/env python3
"""The hidden bench for the Tuck applet (bench before live, F-51): a screen-less Sway, a tiled
window with a floating one over it, the real applet. Focus the tiled one: the floating one must be
tucked away (Sway's scratchpad); a dialog of the same app must stay; bringing the tucked one back
must work and stay (no tuck/untuck loop); the applet must stay light.

    tuck-bench.py            exit 0 when every check passes
"""
from __future__ import annotations

import json, os, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
WINDOW = ("import gi, sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
          "GLib.set_prgname(sys.argv[1]); w=Gtk.Window(); w.set_title(sys.argv[1]); w.show_all(); "
          "GLib.timeout_add_seconds(60, Gtk.main_quit); Gtk.main()")


def main() -> int:
    base = Path(tempfile.mkdtemp(prefix="hftk.", dir="/tmp"))
    run = base / "r"; run.mkdir(mode=0o700)
    (base / "sway.conf").write_text("output HEADLESS-1 resolution 1920x1080\nxwayland disable\n"
                                    'for_window [app_id="floaty"] floating enable, resize set 800 500, move position center\n'
                                    'for_window [title="Save as"] floating enable, resize set 700 400, move position center\n')
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY")}
    env.update(XDG_RUNTIME_DIR=str(run), WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1",
               WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland")
    log = open(base / "bench.log", "w")
    procs, results = [], []
    check = lambda ok, what: (results.append(ok), print(("  ok    " if ok else "  FAIL  ") + what))
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    try:
        time.sleep(2)
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        def msg(*words):
            return subprocess.run(["swaymsg", *words], env=env, capture_output=True, text=True).stdout

        def tree():
            return json.loads(msg("-t", "get_tree", "-r"))

        def where(app):
            def walk(n, ws=None):
                if n.get("type") == "workspace":
                    ws = n["name"]
                if n.get("app_id") == app:
                    return ws
                for c in n.get("nodes", []) + n.get("floating_nodes", []):
                    r = walk(c, ws)
                    if r:
                        return r
            return walk(tree())

        def where_title(title):
            def walk(n, ws=None):
                if n.get("type") == "workspace":
                    ws = n["name"]
                if n.get("name") == title and n.get("pid"):
                    return ws
                for c in n.get("nodes", []) + n.get("floating_nodes", []):
                    r = walk(c, ws)
                    if r:
                        return r
            return walk(tree())

        tuck = subprocess.Popen([sys.executable, str(HERE / "applets/tuck/hypeforge-tuck")], env=env, stdout=log, stderr=log)
        procs.append(tuck)
        for app in ("tiled-app", "floaty"):
            procs.append(subprocess.Popen([sys.executable, "-c", WINDOW, app], env=env, stdout=log, stderr=log))
            time.sleep(1.2)
        check(where("floaty") == "1", "the setup: a floating window over a tiled one, on the screen")
        msg('[app_id="tiled-app"] focus'); time.sleep(0.8)
        check(where("floaty") == "__i3_scratch", "a click on the tiled window tucks the floating one away")
        msg('[app_id="floaty"] scratchpad show'); time.sleep(0.8)
        check(where("floaty") == "1", "bringing it back puts it on screen (Win + − / its taskbar icon)")
        time.sleep(1.5)
        check(where("floaty") == "1", "and it stays (no tuck-and-bring-back loop)")
        # a dialog of the same app as the tiled window: same pid would need one process; same app_id is enough
        procs.append(subprocess.Popen([sys.executable, "-c", WINDOW.replace("w.set_title(sys.argv[1])", "w.set_title('Save as')"), "tiled-app"],
                                      env=env, stdout=log, stderr=log))
        time.sleep(1.2)
        check(where_title("Save as") == "1", "the setup: a floating dialog of the tiled app, on the screen")
        msg('[app_id="tiled-app" tiling] focus'); time.sleep(0.8)
        check(where_title("Save as") == "1", "a click on its app's window leaves the dialog on screen (dialogs never vanish)")
        cpu = sum(int(x) for x in Path(f"/proc/{tuck.pid}/stat").read_text().rsplit(")", 1)[1].split()[11:13]) / os.sysconf("SC_CLK_TCK")
        check(tuck.poll() is None and cpu < 2.0, f"the applet is alive and light ({cpu:.2f} s of processor time)")
    finally:
        for p in procs:
            p.terminate()
        sway.terminate()
    print(f"\nRESULT: {sum(results)}/{len(results)} passed")
    return 0 if results and all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
