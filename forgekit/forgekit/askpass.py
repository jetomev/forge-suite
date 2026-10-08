"""The password, asked inside the app (v0.6.0).

sudo can ask for the password through a helper program instead of the
terminal (``sudo -A`` runs the program named by ``SUDO_ASKPASS``). Until now
Forge apps pointed it at a desktop window (ksshaskpass), which a text console
does not have and which pulled the eye out of the app (Javier, 4 Oct 2026:
asking in a window-manager window "doesn't make sense" for a terminal app).

``PasswordBridge`` makes the app itself that helper. It opens a private
socket (a folder only this user can enter, a random one-time token), writes a
three-line helper script beside it, and hands the program it runs the
environment that points sudo there. When sudo needs the password it runs the
helper; the helper asks the app over the socket; the app shows
``PasswordDialog``; the answer goes back the same way, to sudo only. Nothing
is written to disk, put on a command line or logged. Works the same on a
desktop, on a text console and over ssh.

Run as a program (``python askpass.py <prompt>``) this file is the helper:
standard library only, so it starts fast and needs nothing installed.
"""

from __future__ import annotations

import json
import os
import socket
import sys

SOCK_ENV = "FORGEKIT_ASKPASS_SOCK"
TOKEN_ENV = "FORGEKIT_ASKPASS_TOKEN"


def _client(argv: list[str]) -> int:
    """The helper sudo runs: ask the app, print the password for sudo."""
    prompt = " ".join(argv[1:]) or "Password:"
    path, token = os.environ.get(SOCK_ENV), os.environ.get(TOKEN_ENV)
    if not path or not token:
        print("forgekit-askpass: not started by a Forge app", file=sys.stderr)
        return 1
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(path)
            s.sendall((json.dumps({"token": token, "prompt": prompt}) + "\n").encode())
            data = b""
            while not data.endswith(b"\n"):
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
    except OSError as e:
        print(f"forgekit-askpass: the app could not be reached ({e.strerror or e})", file=sys.stderr)
        return 1
    try:
        answer = json.loads(data or b"{}")
    except ValueError:
        return 1
    if not answer.get("ok"):
        return 1
    sys.stdout.write(answer.get("password", "") + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(_client(sys.argv))


# ── the app's side ──────────────────────────────────────────────────────────
import asyncio  # noqa: E402
import secrets  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
from typing import Awaitable, Callable  # noqa: E402

from textual.app import ComposeResult  # noqa: E402
from textual.binding import Binding  # noqa: E402
from textual.containers import Horizontal, Vertical  # noqa: E402
from textual.widgets import Button, Static  # noqa: E402

from .dialogs import ForgeModal  # noqa: E402

Asker = Callable[[str, int], Awaitable[str | None]]


class PasswordBridge:
    """The socket and the helper sudo runs. ``env()`` is what the program
    started in the app gets; ``asker(prompt, attempt)`` shows the dialog."""

    def __init__(self, asker: Asker) -> None:
        self._asker = asker
        base = os.environ.get("XDG_RUNTIME_DIR")
        if not base or not os.access(base, os.W_OK):
            base = None
        self.dir = tempfile.mkdtemp(prefix="forgekit-", dir=base)    # 0700: only this user
        self.sock = os.path.join(self.dir, "askpass.sock")
        self.helper = os.path.join(self.dir, "askpass")
        self.token = secrets.token_hex(32)
        self.attempts = 0
        self._last_answer = 0.0
        self._server: asyncio.AbstractServer | None = None
        self._pending: set[asyncio.Task] = set()
        here = os.path.abspath(__file__)
        with open(os.open(self.helper, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o700), "w") as f:
            f.write(f'#!/bin/sh\nexec "{sys.executable}" "{here}" "$@"\n')

    async def start(self) -> None:
        self._server = await asyncio.start_unix_server(self._serve, path=self.sock)
        os.chmod(self.sock, 0o600)

    def env(self) -> dict[str, str]:
        return {"SUDO_ASKPASS": self.helper, SOCK_ENV: self.sock, TOKEN_ENV: self.token}

    async def _serve(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        reply = {"ok": False}
        try:
            line = await reader.readline()
            req = json.loads(line or b"{}")
            if secrets.compare_digest(str(req.get("token", "")), self.token):
                # sudo asks again a moment after a wrong password (after its ~2 s
                # failure delay); a request long after the last answer is a new one
                import time
                again = time.monotonic() - self._last_answer < 8
                self.attempts = self.attempts + 1 if again else 1
                ask = asyncio.ensure_future(self._asker(str(req.get("prompt", "")), self.attempts))
                self._pending.add(ask)
                try:
                    pw = await ask
                except asyncio.CancelledError:
                    pw = None
                finally:
                    self._pending.discard(ask)
                self._last_answer = time.monotonic()
                if pw is not None:
                    reply = {"ok": True, "password": pw}
        except (ValueError, OSError):
            pass
        try:
            writer.write((json.dumps(reply) + "\n").encode())
            await writer.drain()
        finally:
            writer.close()
            reply.clear()

    async def close(self) -> None:
        """Stop: a question still open is answered "no password", never left hanging."""
        for ask in list(self._pending):
            ask.cancel()
        if self._server is not None:
            self._server.close()
            try:
                await asyncio.wait_for(self._server.wait_closed(), 2)
            except (asyncio.TimeoutError, OSError):
                pass
            self._server = None
        shutil.rmtree(self.dir, ignore_errors=True)


def prompt_words(prompt: str) -> str:
    """sudo's prompt in plain words: "[sudo] password for javier: " → who it is for."""
    p = prompt.strip()
    if p.startswith("[sudo] password for "):
        who = p.removeprefix("[sudo] password for ").rstrip(": ")
        return f"Your password ({who}), so the change can run as administrator."
    return p.rstrip(":") or "Password"


class PasswordDialog(ForgeModal[str | None]):
    """The password, typed inside the app. Enter confirms, Esc cancels.

    v0.8.0: the dots are centred (``PasswordField``). sudoForge's layout (its
    D-2) is there for any app that wants it: ``heading`` (a bar with who is
    asking), ``detail`` (the command, in the "changed" colour), ``note`` (a
    quieter line) and ``label`` (the line over the field, e.g. "Password for
    javier"). Given a heading, every line is centred and a blank line comes
    before the label. Without them the box looks as it did, dots centred.
    """

    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, prompt: str, attempt: int = 1, title: str = "Password", words: str | None = None,
                 *, heading: str | None = None, detail: str | None = None,
                 note: str | None = None, label: str | None = None) -> None:
        super().__init__()
        self._prompt, self._attempt, self._title = prompt, attempt, title
        self._words = words
        self._heading, self._detail, self._note, self._label = heading, detail, note, label

    def compose(self) -> ComposeResult:
        from .console import literal
        from .password_field import PasswordField
        laid = " -laid-out" if self._heading else ""
        with Vertical(classes="forge-confirm forge-password" + laid):
            yield Static(f"[b]{self._title}[/]", classes="forge-panel-title")
            if self._attempt > 1:
                yield Static("[$forge-warn]That password didn't work. Try again.[/]", id="pw-again")
            if self._heading:
                yield Static(literal(self._heading), id="pw-heading")
            if self._detail:
                yield Static(literal(self._detail), id="pw-detail")
            words = self._words or (None if self._heading else prompt_words(self._prompt))
            if words:
                yield Static(literal(words), classes="forge-confirm-msg", id="pw-words")
            if self._note:
                yield Static(literal(self._note), id="pw-note")
            if self._label:
                yield Static(literal(self._label), id="pw-label")
            yield PasswordField("password", id="pw-input")
            with Horizontal(classes="forge-buttons"):
                yield Button("Cancel (Esc)", id="pw-cancel")
                yield Button("OK (Enter)", id="pw-ok", variant="primary")

    def _field(self):
        from .password_field import PasswordField
        return self.query_one("#pw-input", PasswordField)

    def on_mount(self) -> None:
        from .password_field import PasswordField
        for field in self.query("#pw-input").results(PasswordField):   # gone if closed while opening
            field.focus()

    def on_password_field_submitted(self, event) -> None:
        event.stop()
        self._done(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "pw-ok":
            self._done(self._field().value)
        else:
            self.action_cancel()

    def _done(self, value: str) -> None:
        self._field().clear()
        self.dismiss(value)

    def action_cancel(self) -> None:
        self._field().clear()
        self.dismiss(None)
