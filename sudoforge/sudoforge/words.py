"""Who is asking, for what, in plain words — the box's lines (D-2).

Everything here reads ``/proc`` and strings; nothing asks the system for
anything, so it is all testable with a fake ``/proc``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# polkit's request kinds (the "action id") → the name a person knows.
# The longest matching start wins; anything else is named after the program.
ACTION_NAMES = {
    "org.freedesktop.udisks2.": "USB drives",
    "org.freedesktop.UDisks2.": "USB drives",
    "org.opensuse.cupspkhelper.": "Printers",
    "org.freedesktop.cups.": "Printers",
    "org.freedesktop.NetworkManager.": "Network",
    "org.freedesktop.systemd1.": "System services",
    "org.freedesktop.login1.": "Power",
    "org.freedesktop.packagekit.": "Software",
    "org.freedesktop.timedate1.": "Date and time",
    "org.freedesktop.hostname1.": "Computer name",
    "org.freedesktop.locale1.": "Language",
    "org.freedesktop.accounts.": "User accounts",
    "org.freedesktop.fwupd.": "Firmware updates",
    "org.bluez.": "Bluetooth",
    "org.kognogos.": "Forge Suite",
}

# programs that only pass a request along: look one step further up
PASSERS = {"bash", "sh", "fish", "zsh", "dash", "env", "setsid", "timeout", "nohup",
           "sudo", "pkexec", "runuser", "su", "xargs", "make", "python", "python3"}

PROGRAM_NAMES = {
    "claude": "Claude", "alacritty": "Terminal (Alacritty)", "foot": "Terminal (foot)",
    "kitty": "Terminal (kitty)", "nog": "nog", "nogforge": "nogForge", "grubforge": "grubForge",
    "udiskie": "udiskie", "system-config-printer": "system-config-printer", "yay": "yay",
    "paru": "paru", "makepkg": "makepkg", "pacman": "pacman",
}

TERMINALS = {"alacritty", "foot", "kitty", "konsole", "wezterm-gui", "gnome-terminal-", "xterm"}


@dataclass
class Lines:
    """The box's text, top to bottom (forgekit ``PasswordDialog``'s pieces)."""
    heading: str
    words: str | None
    detail: str | None
    note: str
    label: str


# ── /proc, through one root so tests can fake it ─────────────────────────────
class Procs:
    def __init__(self, root: str | os.PathLike = "/proc") -> None:
        self.root = Path(root)

    def cmdline(self, pid: int) -> list[str]:
        try:
            raw = (self.root / str(pid) / "cmdline").read_bytes()
        except OSError:
            return []
        return [p.decode(errors="replace") for p in raw.split(b"\0") if p]

    def comm(self, pid: int) -> str:
        try:
            return (self.root / str(pid) / "comm").read_text().strip()
        except OSError:
            return ""

    def parent(self, pid: int) -> int:
        try:
            stat = (self.root / str(pid) / "stat").read_text()
            return int(stat.rsplit(")", 1)[1].split()[1])      # the name may hold spaces
        except (OSError, IndexError, ValueError):
            return 0

    def program(self, pid: int) -> str:
        """The program's own name: the file run, else the process name."""
        cmd = self.cmdline(pid)
        if cmd:
            base = os.path.basename(cmd[0])
            if base in ("python", "python3") and len(cmd) > 1 and not cmd[1].startswith("-"):
                return os.path.basename(cmd[1]).removesuffix(".py")
            return base
        return self.comm(pid)


def asker(procs: Procs, pid: int, steps: int = 6) -> tuple[str, str]:
    """(the program behind the request, the terminal it runs in or "").

    Walks up from ``pid`` past programs that only pass requests along (shells,
    sudo, setsid…), so `nog → sudo` names nog and Claude's shell names Claude.
    """
    who, term = "", ""
    seen = 0
    while pid > 1 and seen < 20:
        seen += 1
        name = procs.program(pid)
        if not term and name in TERMINALS:
            term = PROGRAM_NAMES.get(name, name)
        if not who and name and name not in PASSERS and name not in TERMINALS:
            who = name
        if who and term:
            break
        if not who and seen > steps:
            break
        pid = procs.parent(pid)
    return (PROGRAM_NAMES.get(who, who) if who else "A command"), term


def sudo_command(argv: list[str]) -> str:
    """sudo's command line minus sudo and its own options: what will run as admin."""
    if not argv:
        return ""
    takes_value = {"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-T", "-U", "--user", "--group",
                   "--host", "--prompt", "--close-from", "--chdir", "--role", "--type",
                   "--command-timeout", "--other-user"}
    i = 1 if os.path.basename(argv[0]) == "sudo" else 0
    while i < len(argv):
        a = argv[i]
        if a == "--":
            i += 1
            break
        if not a.startswith("-") or a == "-":
            break
        i += 2 if (a in takes_value) else 1
    return " ".join(argv[i:])


def plain_message(message: str) -> str:
    """polkit's sentence, shortened the way the design shows it ("To mount …")."""
    m = message.strip()
    for start in ("Authentication is required to ", "Authentication is needed to "):
        if m.startswith(start):
            rest = m[len(start):].rstrip(".")
            return f"To {rest}."
    return m


def name_for_action(action_id: str) -> str | None:
    best = ""
    for prefix in ACTION_NAMES:
        if action_id.startswith(prefix) and len(prefix) > len(best):
            best = prefix
    return ACTION_NAMES[best] if best else None


def polkit_lines(action_id: str, message: str, details: dict, user: str,
                 procs: Procs | None = None) -> Lines:
    """The box for polkit's admin pop-up (design screens 1, 2 and 4)."""
    procs = procs or Procs()
    pid = int(details.get("polkit.subject-pid") or details.get("polkit.caller-pid") or 0)
    who, _term = asker(procs, pid) if pid else ("A program", "")
    detail = None
    if action_id == "org.freedesktop.policykit.exec":            # pkexec: show what will run
        caller = int(details.get("polkit.caller-pid") or 0)
        cmd = procs.cmdline(caller) if caller else []
        if cmd and os.path.basename(cmd[0]) == "pkexec":
            rest = [a for a in cmd[1:]]
            while rest and rest[0].startswith("--"):
                rest.pop(0)
            detail = " ".join(rest) or None
        name = who
        heading = f"{name} wants to run as admin"
    else:
        name = name_for_action(action_id) or who
        heading = f"{name} wants admin rights"
    note = f"Asked by {who} · checked by the system (polkit)"
    return Lines(heading=heading, words=plain_message(message), detail=detail, note=note,
                 label=f"Password for {user}")


def sudo_lines(sudo_pid: int, user: str, procs: Procs | None = None) -> Lines:
    """The box for `sudo -A` (design screen 3): the command, in orange, under the title."""
    procs = procs or Procs()
    who, term = asker(procs, procs.parent(sudo_pid))
    command = sudo_command(procs.cmdline(sudo_pid))
    note = f"Started from {term} · checked by sudo" if term else "Checked by sudo"
    return Lines(heading=f"{who} wants to run as admin", words=None, detail=command or None,
                 note=note, label=f"Password for {user}")
