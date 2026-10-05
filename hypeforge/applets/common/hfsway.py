"""hypeForge applets · talking to Sway over its own socket (the i3 IPC protocol).

Shared by every applet, Python standard library only.
"""

import json
import os
import socket
import struct
import sys

MAGIC = b"i3-ipc"
RUN_COMMAND, GET_WORKSPACES, SUBSCRIBE = 0, 1, 2
GET_TREE = 4
EVENT_WORKSPACE = 0x80000000
EVENT_WINDOW = 0x80000003


class Sway:
    def __init__(self):
        path = os.environ.get("SWAYSOCK")
        if not path:
            sys.exit("hypeforge-workspaces: SWAYSOCK is not set — is this running inside Sway?")
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(path)

    def _read(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Sway closed the connection")
            data += chunk
        return data

    def send(self, kind, payload=""):
        body = payload.encode()
        self.sock.sendall(MAGIC + struct.pack("=II", len(body), kind) + body)

    def receive(self):
        header = self._read(len(MAGIC) + 8)
        length, kind = struct.unpack("=II", header[len(MAGIC):])
        return kind, json.loads(self._read(length))

    def ask(self, kind, payload=""):
        self.send(kind, payload)
        return self.receive()[1]

    def run(self, *commands):
        return self.ask(RUN_COMMAND, "; ".join(commands))


def quoted(s):
    return '"' + s.replace('"', '\\"') + '"'
