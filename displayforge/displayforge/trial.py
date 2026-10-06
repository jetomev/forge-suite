"""displayForge · try a change live, and undo it by itself unless kept.

"Never leave a screen black" (CLAUDE.md): a changed mode can leave a screen dark, and then the
person cannot see the question. So the undo does not live only in displayForge: `start()` also
launches an independent safety timer — a separate process — that runs the undo when the time
is up unless `keep()` was called. If displayForge freezes, crashes or is closed meanwhile, the
screens still come back.
"""

from __future__ import annotations

import os
import shlex
import signal
import subprocess
import tempfile
from pathlib import Path

from . import screens as S

SECONDS = 12  # the design's countdown


def run(cmds: list[str], swaymsg: str = "swaymsg") -> bool:
    """Send commands to Sway in one message; True if Sway accepted them all."""
    if not cmds:
        return True
    out = subprocess.run([swaymsg, "; ".join(cmds)], capture_output=True, text=True)
    return out.returncode == 0


class Trial:
    def __init__(self, before: list[S.Screen], after: list[S.Screen], seconds: int = SECONDS,
                 swaymsg: str = "swaymsg", runtime: str | None = None):
        self.before, self.after = before, after
        self.seconds = seconds
        self.swaymsg = swaymsg
        self.forward = S.all_commands(before, after)
        self.back = S.all_commands(after, before)
        base = Path(runtime or os.environ.get("XDG_RUNTIME_DIR", tempfile.gettempdir()))
        self.keepfile = base / f"displayforge-keep-{os.getpid()}"
        self.watchdog: subprocess.Popen | None = None

    def start(self) -> bool:
        """Apply the change and arm the safety timer. False (and nothing changed) if Sway refused."""
        self.keepfile.unlink(missing_ok=True)
        undo = shlex.quote("; ".join(self.back))
        script = (f"sleep {int(self.seconds)}; "
                  f"[ -e {shlex.quote(str(self.keepfile))} ] || {shlex.quote(self.swaymsg)} {undo}")
        if self.back:
            self.watchdog = subprocess.Popen(["sh", "-c", script], start_new_session=True,
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not run(self.forward, self.swaymsg):
            self.revert_now()
            return False
        return True

    def keep(self) -> None:
        """The person said "Keep it": disarm the safety timer."""
        self.keepfile.touch()
        self._stop_watchdog()
        self.keepfile.unlink(missing_ok=True)

    def revert_now(self) -> None:
        """"Go back now" (or the in-app countdown ran out): undo at once, disarm the timer."""
        self._stop_watchdog()
        run(self.back, self.swaymsg)

    def settle(self) -> None:
        """After the time ran out with nobody answering: the safety timer has undone the change;
        collect its finished process (no zombie left behind)."""
        if self.watchdog:
            self.watchdog.wait(timeout=self.seconds + 5)
            self.watchdog = None

    def _stop_watchdog(self) -> None:
        if self.watchdog and self.watchdog.poll() is None:
            try:
                os.killpg(self.watchdog.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            self.watchdog.wait(timeout=2)
        self.watchdog = None
