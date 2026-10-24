#!/usr/bin/env python3
"""The Workspaces applet while screens are switched off and back on — a monitor unplugged, or a screen
turned off in displayForge (KognogOS stage 03, 2026-10-24: before Javier tries one and two screens on
his own desktop by switching screens off).

A screen-less Sway with three fake screens and the applet from the repository; three test windows;
then screen 3 off, screen 2 off (one screen left), 2 back on, 3 back on. After each step: the applet
still running, the screens steady (what each shows doesn't keep changing), all three windows still
there. Nothing touches the real desktop.

    python3 scripts/screens-off-bench.py      exit 0 = all good
"""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
APPLET = Path(__file__).resolve().parent.parent / "applets/workspaces/hypeforge-workspaces"
base = Path(tempfile.mkdtemp(prefix="wsoff."))
run, conf = base / "run", base / "c"; run.mkdir(mode=0o700); (conf / "hypeforge/applets").mkdir(parents=True)
S = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]
(conf / "hypeforge/applets/workspaces.toml").write_text('enabled = true\nscreens = ' + json.dumps(S) + '\n'
    + "".join(f'[[workspace]]\nname = "{n}"\n' for n in ("Daily", "Work", "Entertainment", "Gaming")) + "[share]\n")
(base / "sway.conf").write_text("".join(f"output {s} resolution 1280x720 position {i*1280} 0\n" for i, s in enumerate(S)) + "xwayland disable\n")
env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
           WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1")
log = open(base / "log", "w")
procs = [subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)]
for _ in range(100):
    s = list(run.glob("sway-ipc.*.sock"))
    if s: env["SWAYSOCK"] = str(s[0]); break
    time.sleep(0.1)
env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
msg = lambda *a: json.loads(subprocess.run(["swaymsg", "-r", *a], env=env, capture_output=True, text=True).stdout or "null")
procs.append(subprocess.Popen([sys.executable, str(APPLET)], env=env, stdout=log, stderr=log))
time.sleep(2)
W = ("import gi,sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk,GLib; GLib.set_prgname(sys.argv[1]); "
     "w=Gtk.Window(title=sys.argv[1]); w.show_all(); GLib.timeout_add_seconds(120, Gtk.main_quit); Gtk.main()")
for a in ("win-a", "win-b", "win-c"):
    procs.append(subprocess.Popen([sys.executable, "-c", W, a], env={**env, "GDK_BACKEND": "wayland"}, stdout=log, stderr=log))
time.sleep(3)
def apps():
    out = []
    def walk(n):
        if n.get("app_id"): out.append(n["app_id"])
        for c in n.get("nodes", []) + n.get("floating_nodes", []): walk(c)
    walk(msg("-t", "get_tree")); return sorted(out)
def visible(): return sorted(w["name"] for w in msg("-t", "get_workspaces") if w["visible"])
ok = True
def step(words, cmd=None):
    global ok
    if cmd: subprocess.run(["swaymsg", cmd], env=env, capture_output=True)
    time.sleep(3)
    a = visible(); time.sleep(3); b = visible()
    alive = procs[1].poll() is None; wins = apps()
    good = alive and a == b and wins == ["win-a", "win-b", "win-c"]
    ok &= good
    print(f"{'ok  ' if good else 'FAIL'} {words}: applet alive {alive}, steady {a == b}, windows {len(wins)}/3, showing {b}")
step("three screens")
step("HEADLESS-3 off", "output HEADLESS-3 disable")
step("HEADLESS-2 off too (one screen)", "output HEADLESS-2 disable")
step("HEADLESS-2 back on", "output HEADLESS-2 enable")
step("HEADLESS-3 back on", "output HEADLESS-3 enable")
print("RESULT:", "OK" if ok else f"FAILED | the bench folder is kept: {base}")
subprocess.run(["swaymsg", "exit"], env=env, capture_output=True)
for p in procs[1:]: p.terminate()
for p in procs:
    try: p.wait(5)
    except subprocess.TimeoutExpired: p.kill()
if ok: shutil.rmtree(base, ignore_errors=True)
sys.exit(0 if ok else 1)
