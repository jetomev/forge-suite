#!/usr/bin/env python3
"""nightForge — run with `python main.py`, or `nightforge` once installed.

    nightforge              the app (Night Light and Schedule)
    nightforge start        what hypeForge runs at login: the night light as your settings say,
                            and the tray icon
    nightforge tray         the tray icon on its own
    nightforge status       what the night light is doing now, in one line
"""

import os
import subprocess
import sys


def start() -> int:
    from nightforge import control, tray
    from nightforge.settings import Settings
    s = Settings.load()
    code = 0
    try:
        control.start(s, "auto")
    except control.Trouble as t:
        print(f"nightforge: {t}", file=sys.stderr)
        code = 1
    if not tray.already_running():
        me = [sys.executable, os.path.abspath(__file__)]
        subprocess.Popen(me + ["tray"], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return code


def status() -> int:
    from nightforge import control
    from nightforge.settings import Settings
    st = control.status(Settings.load())
    print(f"{ {'warm': '☾ warm', 'day': '☀ daylight', 'off': '○ off'}[st['state']] } — {st['why']}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.lower() != "--hypeforge"]
    if args == ["start"]:
        sys.exit(start())
    if args == ["tray"]:
        from nightforge.tray import main as tray_main
        sys.exit(tray_main())
    if args == ["status"]:
        sys.exit(status())
    if args in (["-h"], ["--help"]):
        print(__doc__.strip())
        sys.exit(0)
    if args:
        sys.exit(__doc__.strip())
    from nightforge.app import main
    sys.exit(main())
