"""sudo learns about sudoForge from its own settings file (D-3).

``/etc/sudo.conf`` gets two lines, marked as ours:

    # sudoForge: the password box for `sudo -A` (undo: sudoforge undo)
    Path askpass /usr/lib/sudoforge/sudoforge-askpass

The file belongs to the sudo package and is one of its backup files, so an
update never overwrites it. Applying makes a backup first
(``/etc/sudo.conf.sudoforge-backup``); undo removes only our two lines, so
anything else changed since stays. If another ``Path askpass`` is already
active, nothing is changed and the reason is given. Changing it needs admin
rights: ``sudoforge setup`` asks through polkit (``pkexec``), so the question
comes up in sudoForge's own box.

The text changes are plain functions (tested on strings); ``root_main`` is the
small part that runs as admin.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile

CONF = "/etc/sudo.conf"
BACKUP = "/etc/sudo.conf.sudoforge-backup"
MARK = "# sudoForge: the password box for `sudo -A` (undo: sudoforge undo)"
_ACTIVE_ASKPASS = re.compile(r"^\s*Path\s+askpass\s+(\S+)", re.M)


class Refused(Exception):
    """Nothing was changed; the message says why, in plain words."""


def current_askpass(text: str) -> str | None:
    m = _ACTIVE_ASKPASS.search(text)
    return m.group(1) if m else None


def applied(text: str, helper: str) -> bool:
    return MARK in text and current_askpass(text) == helper


def apply_text(text: str, helper: str) -> str:
    if not os.path.isabs(helper) or any(c in helper for c in "\n\r \t"):
        raise Refused(f"the helper's path must be a plain full path: {helper!r}")
    text = undo_text(text) if MARK in text else text
    other = current_askpass(text)
    if other:
        raise Refused(f"{CONF} already names another password helper ({other}); "
                      "sudoForge leaves it alone. Remove that line first if sudoForge should take over.")
    if text and not text.endswith("\n"):
        text += "\n"
    return text + f"{MARK}\nPath askpass {helper}\n"


def undo_text(text: str) -> str:
    out, lines, i = [], text.splitlines(keepends=True), 0
    while i < len(lines):
        if lines[i].rstrip("\n") == MARK:
            i += 1
            if i < len(lines) and _ACTIVE_ASKPASS.match(lines[i]):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def _write_atomic(path: str, text: str) -> None:
    st = os.stat(path)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".sudo.conf.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.chown(tmp, st.st_uid, st.st_gid)
        os.chmod(tmp, st.st_mode & 0o7777)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def root_main(argv: list[str], conf: str = CONF, backup: str = BACKUP) -> int:
    """Runs as admin (through pkexec): `apply <helper>` or `undo`."""
    try:
        with open(conf) as f:
            text = f.read()
        if argv[:1] == ["apply"] and len(argv) == 2:
            new = apply_text(text, argv[1])
            if new == text:
                print("Already set up; nothing changed.")
                return 0
            shutil.copy2(conf, backup)
            _write_atomic(conf, new)
            print(f"Done: sudo -A now asks in sudoForge's box. Backup: {backup}")
            return 0
        if argv[:1] == ["undo"] and len(argv) == 1:
            new = undo_text(text)
            if new == text:
                print("sudoForge was not set up there; nothing changed.")
                return 0
            _write_atomic(conf, new)
            print(f"Undone: sudoForge's two lines are gone from {conf}; everything else is as it was.")
            return 0
        print("usage: apply <helper path> | undo", file=sys.stderr)
        return 2
    except Refused as e:
        print(f"Nothing changed: {e}", file=sys.stderr)
        return 3
    except OSError as e:
        print(f"Nothing changed: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(root_main(sys.argv[1:]))
