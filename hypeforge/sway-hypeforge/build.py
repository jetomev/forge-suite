#!/usr/bin/env python3
"""Build hypeForge's Sway: the system's Sway version, with our patches (D-111, 2026-10-17).

    build.py [VERSION]          (default: the version of the Sway installed, from pacman)

  1. downloads that release's source and signature from github.com/swaywm/sway (once; kept in
     ~/.cache/hypeforge/sway-build/download/) and checks the signature against Sway's release key
  2. unpacks it fresh and applies every *.patch here, in order — if one no longer fits, it stops and
     says which (the system's own Sway keeps running meanwhile; the login falls back to it)
  3. builds it (meson + ninja, against the system's wlroots) and installs it into
     ~/.local/opt/sway-hypeforge/<version>/, then points ~/.local/opt/sway-hypeforge/current at it

Nothing outside $HOME is touched, and the system's Sway is never replaced: an Arch update of Sway can't
break the login, it only makes this build stale until it is run again (hypeforge-session checks).
Every run logs to hypeforge/logs/sway-build-<time>.log (and sway-build-latest.log).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = HERE.parent / "logs"
CACHE = Path.home() / ".cache/hypeforge/sway-build"
OPT = Path.home() / ".local/opt/sway-hypeforge"
KEY = "34FF9526CFEF0E97A340E2E40FDE7BE0E88F5E48"        # Simon Ser, Sway's release key (checked 10-17)
URL = "https://github.com/swaywm/sway/releases/download/{v}/sway-{v}.tar.gz"


def system_version() -> str:
    out = subprocess.run(["pacman", "-Q", "sway"], capture_output=True, text=True).stdout
    m = re.search(r"sway (?:\d+:)?([\d.]+)-", out)
    if not m:
        sys.exit("build.py: no Sway installed by pacman — give the version: build.py 1.12")
    return m.group(1)


def main() -> int:
    version = sys.argv[1] if len(sys.argv) > 1 else system_version()
    LOGS.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = LOGS / f"sway-build-{stamp}.log"
    log = open(log_path, "w")

    def say(words: str):
        print(words, flush=True)
        log.write(words + "\n")
        log.flush()

    def run(*cmd, cwd=None, check=True):
        log.write("$ " + " ".join(map(str, cmd)) + "\n")
        log.flush()
        r = subprocess.run(list(map(str, cmd)), cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        if check and r.returncode != 0:
            say(f"\nFAILED: {' '.join(map(str, cmd[:3]))}… (exit {r.returncode}); see {log_path}")
            raise SystemExit(1)
        return r.returncode

    latest = LOGS / "sway-build-latest.log"
    latest.unlink(missing_ok=True)
    latest.symlink_to(log_path.name)
    say(f"\nhypeForge's Sway {version}: download · check · patch · build · install\n")

    down = CACHE / "download"
    down.mkdir(parents=True, exist_ok=True)
    tar, sig = down / f"sway-{version}.tar.gz", down / f"sway-{version}.tar.gz.sig"
    for f in (tar, sig):
        if not f.exists():
            say(f"  downloading {f.name}")
            run("curl", "-sSfL", "-o", f, URL.format(v=version) + (".sig" if f == sig else ""))
    r = subprocess.run(["gpg", "--status-fd", "1", "--verify", sig, tar], capture_output=True, text=True)
    if f"VALIDSIG {KEY}" not in r.stdout:
        run("gpg", "--keyserver", "hkps://keys.openpgp.org", "--recv-keys", KEY, check=False)
        r = subprocess.run(["gpg", "--status-fd", "1", "--verify", sig, tar], capture_output=True, text=True)
    if f"VALIDSIG {KEY}" not in r.stdout:
        say("  the signature does NOT check out against Sway's release key — stopping, nothing built")
        return 1
    say("  signature: good (Simon Ser, Sway's release key)")

    src = CACHE / f"src-{version}"
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True)
    run("tar", "xzf", tar, "-C", src, "--strip-components=1")
    for patch in sorted(HERE.glob("*.patch")):
        if run("patch", "-p1", "--dry-run", "-i", patch, cwd=src, check=False) != 0:
            say(f"\n  {patch.name} no longer fits Sway {version}: stopping. The login keeps using the system's")
            say("  Sway (no title bar buttons) until the patch is brought up to date.")
            return 2
        run("patch", "-p1", "-i", patch, cwd=src)
        say(f"  patched: {patch.name}")

    prefix = OPT / version
    run("meson", "setup", "build", f"--prefix={prefix}", "-Dman-pages=disabled", "-Dwerror=false",
        "--buildtype=release", cwd=src)
    say("  building…")
    run("ninja", "-C", "build", cwd=src)
    run("ninja", "-C", "build", "install", cwd=src)
    current = OPT / "current"
    tmp = OPT / ".current.tmp"
    tmp.unlink(missing_ok=True)
    tmp.symlink_to(version)
    tmp.replace(current)
    out = subprocess.run([prefix / "bin/sway", "--version"], capture_output=True, text=True).stdout.strip()
    say(f"  installed: {prefix} ({out})")
    say(f"\nDone. hypeForge's Sway {version} is ready; the next \"Sway (hypeForge buttons)\" login uses it.")
    say(f"Logs: {log_path}\n\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
