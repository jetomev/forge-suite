"""The sudoForge service: runs for the whole Sway session, no window.

Two doors in, one box out:

* **sudo** — `sudoforge-askpass` connects to ``service.sock`` in a private
  folder (``$XDG_RUNTIME_DIR/sudoforge``, 0700). The service checks the caller
  is this user (SO_PEERCRED), finds sudo as the helper's parent, and builds the
  box's lines from it (never from what the helper claims).
* **polkit** — an authentication agent registered for the login session
  (``Polkit.UnixSession``), so every program's admin request comes here.
  Adapted from forgekit's ``InAppPolkitAgent`` (0.6.0), which answers for its
  own app only; polkit's setuid helper (``PolkitAgent.Session``) checks the
  password, never sudoForge.

The box is a separate program (``sudoforge.box``) in its own small terminal
window, started per question with a one-time socket and token passed in its
environment (never on a command line). One box at a time; a cancelled request
closes its box. The password exists only in memory, on its way through.
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable

from .words import Lines, Procs, polkit_lines, sudo_lines

TRIES = 3
SPAWN_TIMEOUT = 20          # seconds for the box window to come up and connect
HERE = Path(__file__).resolve().parent.parent


def runtime_dir() -> Path:
    return Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}") / "sudoforge"


def box_command() -> list[str]:
    """The box's window. ``SUDOFORGE_BOX_COMMAND`` replaces it (tests: a stand-in box)."""
    override = os.environ.get("SUDOFORGE_BOX_COMMAND")
    if override:
        return override.split()
    return ["alacritty", "--class", "sudoforge",
            "-o", "window.dimensions.columns=66", "-o", "window.dimensions.lines=24",
            "-e", sys.executable, "-m", "sudoforge.box"]


def log(msg: str) -> None:
    """The service's record: what happened, never a password."""
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def peer(conn: socket.socket) -> tuple[int, int]:
    """(pid, uid) of the program on the other end of a Unix socket."""
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    pid, uid, _gid = struct.unpack("3i", raw)
    return pid, uid


def read_line(conn: socket.socket, limit: int = 65536) -> dict:
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(data) > limit:
            raise ValueError("too long")
    return json.loads(data or b"{}")


def send_line(conn: socket.socket, obj: dict) -> None:
    conn.sendall((json.dumps(obj) + "\n").encode())


# ── the box: one at a time ───────────────────────────────────────────────────
class Box:
    """One question, one window. ``ask()`` blocks until an answer or a cancel."""

    def __init__(self, folder: Path, lines: Lines, attempt: int) -> None:
        self.folder, self.lines, self.attempt = folder, lines, attempt
        self._cancelled = threading.Event()
        self._proc: subprocess.Popen | None = None
        self._conn: socket.socket | None = None

    def cancel(self) -> None:
        self._cancelled.set()
        for close in (lambda: self._conn and self._conn.shutdown(socket.SHUT_RDWR),
                      lambda: self._proc and self._proc.terminate()):
            try:
                close()
            except OSError:
                pass

    def ask(self) -> str | None:
        token = secrets.token_hex(16)
        path = self.folder / f"box-{secrets.token_hex(6)}.sock"
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            srv.bind(str(path))
            os.chmod(path, 0o600)
            srv.listen(1)
            srv.settimeout(0.25)
            env = dict(os.environ, SUDOFORGE_BOX_SOCK=str(path), SUDOFORGE_BOX_TOKEN=token,
                       PYTHONPATH=os.pathsep.join(filter(None, [str(HERE), os.environ.get("PYTHONPATH")])))
            self._proc = subprocess.Popen(box_command(), env=env, stdin=subprocess.DEVNULL,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                          start_new_session=True)
            end = time.monotonic() + SPAWN_TIMEOUT
            while True:                                   # wait for the window to call back
                if self._cancelled.is_set() or time.monotonic() > end or self._proc.poll() is not None:
                    return None
                try:
                    conn, _ = srv.accept()
                    break
                except socket.timeout:
                    continue
            self._conn = conn
            conn.settimeout(None)
            if peer(conn)[1] != os.getuid():
                return None
            hello = read_line(conn)
            if not secrets.compare_digest(str(hello.get("token", "")), token):
                return None
            send_line(conn, {"heading": self.lines.heading, "words": self.lines.words,
                             "detail": self.lines.detail, "note": self.lines.note,
                             "label": self.lines.label, "attempt": self.attempt})
            reply = read_line(conn)
            if self._cancelled.is_set() or not reply.get("ok"):
                return None
            pw = reply.get("password")
            reply.clear()
            return pw if isinstance(pw, str) else None
        except (OSError, ValueError):
            return None
        finally:
            for c in (self._conn, srv):
                try:
                    c and c.close()
                except OSError:
                    pass
            try:
                path.unlink()
            except OSError:
                pass
            if self._proc and self._proc.poll() is None:
                try:
                    self._proc.wait(2)
                except subprocess.TimeoutExpired:
                    self._proc.terminate()


class Service:
    def __init__(self, folder: Path | None = None, procs: Procs | None = None) -> None:
        self.folder = folder or runtime_dir()
        self.procs = procs or Procs()
        self.user = os.environ.get("USER") or str(os.getuid())
        self._one_at_a_time = threading.Lock()
        self._current: Box | None = None
        self._server: socket.socket | None = None
        self._stop = threading.Event()
        self._sudo_tries: dict[int, tuple[int, float]] = {}     # sudo pid → (attempt, last answer)
        self.agent = None

    # ── the private folder and the sudo door ────────────────────────────────
    def prepare(self) -> None:
        self.folder.mkdir(mode=0o700, parents=True, exist_ok=True)
        st = self.folder.stat()
        if st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o700:
            os.chmod(self.folder, 0o700)
            if self.folder.stat().st_uid != os.getuid():
                raise PermissionError(f"{self.folder} is not this user's")
        for old in self.folder.glob("*.sock"):
            old.unlink()

    def open_sudo_door(self) -> None:
        path = self.folder / "service.sock"
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(str(path))
        os.chmod(path, 0o600)
        self._server.listen(8)
        threading.Thread(target=self._accept_loop, name="sudoforge-sudo", daemon=True).start()

    def _accept_loop(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _ = self._server.accept()
            except OSError:
                return
            threading.Thread(target=self._handle_sudo, args=(conn,), daemon=True).start()

    def _handle_sudo(self, conn: socket.socket) -> None:
        reply: dict = {"ok": False}
        try:
            pid, uid = peer(conn)
            if uid != os.getuid():
                return
            req = read_line(conn)
            if req.get("kind") != "sudo":
                return
            sudo_pid = self.procs.parent(pid)
            if os.path.basename((self.procs.cmdline(sudo_pid) or [""])[0]) != "sudo":
                reply["reason"] = "only sudo may ask here"
                log(f"refused a request from pid {pid}: its parent is not sudo")
                return
            # the same sudo asking again means the last password was wrong
            attempt = self._sudo_tries.get(sudo_pid, (0, 0.0))[0] + 1
            lines = sudo_lines(sudo_pid, self.user, self.procs)
            log(f"sudo asks (try {attempt}): {lines.detail or '?'}")
            pw = self.ask(lines, attempt)
            self._sudo_tries[sudo_pid] = (attempt, time.monotonic())
            self._forget_old_sudos()
            if pw is not None:
                reply = {"ok": True, "password": pw}
                log("sudo: answered")
            else:
                log("sudo: cancelled")
        except (OSError, ValueError):
            pass
        finally:
            try:
                send_line(conn, reply)
            except OSError:
                pass
            reply.clear()
            conn.close()

    def _forget_old_sudos(self) -> None:
        for pid in [p for p in self._sudo_tries if not (self.procs.root / str(p)).exists()]:
            self._sudo_tries.pop(pid, None)

    # ── the box ──────────────────────────────────────────────────────────────
    def ask(self, lines: Lines, attempt: int, cancelled: Callable[[], bool] = lambda: False) -> str | None:
        """Show the box (waiting for any box already open) and return the password or None."""
        with self._one_at_a_time:
            if cancelled() or self._stop.is_set():
                return None
            box = Box(self.folder, lines, attempt)
            self._current = box
            try:
                return box.ask()
            finally:
                self._current = None

    # ── polkit ──────────────────────────────────────────────────────────────
    def start_agent(self) -> str | None:
        """Register for the session; returns why not, or None when it worked."""
        from .agent import SessionAgent
        self.agent = SessionAgent(self)
        return self.agent.start()

    # ── run / stop ──────────────────────────────────────────────────────────
    def stop(self) -> None:
        self._stop.set()
        if self._current:
            self._current.cancel()
        if self.agent:
            self.agent.stop()
        if self._server:
            try:
                self._server.close()
            except OSError:
                pass
        shutil.rmtree(self.folder, ignore_errors=True)


def run() -> int:
    """`sudoforge service`: started at login by hypeForge's Sway config."""
    import signal
    svc = Service()
    if not os.environ.get("SWAYSOCK"):
        log("not a Sway session: sudoForge's box needs the Sway desktop. Nothing started.")
        return 1
    if (svc.folder / "service.sock").exists():
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            probe.connect(str(svc.folder / "service.sock"))
            log("sudoForge is already running in this session. Nothing started.")
            return 0
        except OSError:
            pass
        finally:
            probe.close()
    svc.prepare()
    svc.open_sudo_door()
    log(f"sudo door open: {svc.folder / 'service.sock'}")
    why = svc.start_agent()
    if why:
        log(f"polkit: not registered ({why}); sudo -A still works")
    else:
        log("polkit: answering admin requests for this session")
    from gi.repository import GLib
    loop = GLib.MainLoop()

    def quit_(*_a):
        loop.quit()
        return False
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, quit_)
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, quit_)
    try:
        loop.run()
    finally:
        svc.stop()
        log("stopped; polkit and sudo are back to having no helper here")
    return 0
