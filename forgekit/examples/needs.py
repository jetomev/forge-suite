"""examples/needs.py — the start-up check, shown with a need that is not met.

Run:  PYTHONPATH=. python examples/needs.py            (a required need: Close only)
      PYTHONPATH=. python examples/needs.py optional   (an optional one: Continue anyway appears)

Nothing on this computer is checked for real: the need below always fails, so
the screen can be seen anywhere. A real app writes it like this:

    NEEDS = [sway_session("displayForge arranges your screens by talking to Sway.",
                          "Use your desktop's own display settings instead.")]
    if not start_check("displayForge", NEEDS):
        return 2
"""

from __future__ import annotations

import sys

from forgekit import Need, start_check

optional = len(sys.argv) > 1 and sys.argv[1] == "optional"

NEEDS = [
    Need("a Sway session", lambda: (False, "KDE Plasma (Wayland)"),
         "displayForge arranges your screens by talking to Sway.",
         "Use your desktop's own display settings instead.", optional=optional),
]

if __name__ == "__main__":
    ok = start_check("displayForge", NEEDS)
    print("the app would start now" if ok else "the app did not start")
