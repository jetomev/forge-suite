"""The helper sudo runs for `sudo -A` (D-3: named in /etc/sudo.conf).

sudo runs it as the person, with its prompt as the only argument, and reads
the password from what it prints. It asks the sudoForge service over the
private socket; the service works out who is asking from the connection
itself (the helper's parent is sudo), opens the box, and answers. Standard
library only, so it starts at once and needs nothing installed.

No service (a text console, another desktop, the service stopped): it says so
in plain words and exits 1, so sudo reports "no password was provided" and
nothing runs.
"""

from __future__ import annotations

import json
import os
import socket
import sys


def runtime_dir() -> str:
    return os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"


def service_socket() -> str:
    return os.path.join(runtime_dir(), "sudoforge", "service.sock")


NO_SERVICE = ("sudoForge: there is no password box here (its service runs on the Sway desktop).\n"
              "Run the command without -A to type the password in the terminal.")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    prompt = " ".join(argv[1:]) or "Password:"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(service_socket())
    except OSError:
        print(NO_SERVICE, file=sys.stderr)
        return 1
    try:
        s.sendall((json.dumps({"kind": "sudo", "prompt": prompt}) + "\n").encode())
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        reply = json.loads(data or b"{}")
    except (OSError, ValueError):
        reply = {}
    finally:
        s.close()
    if reply.get("ok") and isinstance(reply.get("password"), str):
        sys.stdout.write(reply["password"] + "\n")
        sys.stdout.flush()
        reply.clear()
        return 0
    if reply.get("reason"):
        print(f"sudoForge: {reply['reason']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
