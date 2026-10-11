"""COSMIC's App Library (D-77 C-4): search on top, every app in a wide grid, your groups (the
launcher's own: Favorites, then the standard groups) as a row of folders below — the Start panel's
own code, laid out COSMIC's way (start.build(library=True))."""

from __future__ import annotations

import panelkit
import start


def build(look: panelkit.Look, args) -> panelkit.Panel:
    return start.build(look, args, view="library", library=True)
