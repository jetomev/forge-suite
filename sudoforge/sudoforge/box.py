"""The box: one question, in its own small floating terminal window (D-2).

Started by the service for each question, with a one-time socket and token in
its environment. It reads the question, shows forgekit's ``PasswordDialog`` in
sudoForge's layout, sends the answer back and closes. If the service cancels
(polkit gave up, the session ends) the socket closes and so does the box.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading

from textual.app import App, ComposeResult
from textual.widgets import Static

from forgekit import FORGE_CSS, PasswordDialog


class BoxApp(App):
    CSS = FORGE_CSS + """
    Screen { background: $forge-bg; }
    .forge-password { width: 62; }
    """
    TITLE = "sudoForge"

    def __init__(self, question: dict, conn: socket.socket) -> None:
        super().__init__()
        self.question, self.conn = question, conn
        self._answered = False

    def compose(self) -> ComposeResult:
        yield Static("")

    def on_mount(self) -> None:
        q = self.question
        attempt = int(q.get("attempt") or 1)
        title = "sudoForge" + (f" · try {attempt} of 3" if attempt > 1 else "")
        self.push_screen(PasswordDialog("", attempt, title, words=q.get("words") or None,
                                        heading=q.get("heading"), detail=q.get("detail"),
                                        note=q.get("note"), label=q.get("label")),
                         self.answered)
        threading.Thread(target=self._watch_service, daemon=True).start()

    def answered(self, value: str | None) -> None:
        self._answered = True
        reply = {"ok": value is not None, "password": value} if value is not None else {"ok": False}
        try:
            self.conn.sendall((json.dumps(reply) + "\n").encode())
        except OSError:
            pass
        reply.clear()
        self.exit()

    def _watch_service(self) -> None:
        """The service closing our socket means: cancelled, close the box."""
        try:
            while self.conn.recv(1):
                pass
        except OSError:
            pass
        if not self._answered:
            self.call_from_thread(self.exit)


def main() -> int:
    path, token = os.environ.pop("SUDOFORGE_BOX_SOCK", ""), os.environ.pop("SUDOFORGE_BOX_TOKEN", "")
    if not path or not token:
        print("sudoForge's box is opened by the sudoForge service, not by hand.", file=sys.stderr)
        return 1
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.connect(path)
    conn.sendall((json.dumps({"token": token}) + "\n").encode())
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(4096)
        if not chunk:
            return 1
        data += chunk
    BoxApp(json.loads(data), conn).run()
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
