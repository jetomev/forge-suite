"""KDE's Kickoff (D-76 K-3): the launcher's groups on the left, the apps as a list with their
descriptions on the right, search at the top, you and the power buttons at the bottom — the Start
panel's own code, laid out as a list (start.build(as_list=True))."""

from __future__ import annotations

import panelkit
import start


def build(look: panelkit.Look, args) -> panelkit.Panel:
    return start.build(look, args, as_list=True, view="kickoff")
