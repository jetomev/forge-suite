"""forgekit — a shared Textual TUI shell for the Forge Suite.

Top menu bar, full-width workspace, and floating dialogs, Catppuccin-themed.
Build an app by subclassing ``ForgeApp``; see ``examples/demo.py``.
"""

from .app import ForgeApp
from .closing import closing_notice, runs_log_row, session_banner
from .flows import ChangeGroup, ProgressDialog, ReviewDialog, review_markup
from .manual import ManualScreen, load_pages
from .pickers import FilterPicker
from .widgets import (
    ChangesBar, CheckList, Choices, HintBar, Notice, NumberPresets, SettingRow, Toggle, hints_markup, notice_markup,
)
from .console import GLYPHS, console_mode, console_text, glyph
from .dialogs import (
    AboutDialog, ConfirmDialog, ForgeModal, ForgePanelScreen, LicenseDialog,
    ShortcutsDialog,
)
from .licenses import GPL3_NOTICE
from .menu import MenuBar, MenuDropdown, accel, underline_label
from .theme import COLORS, FORGE_CSS, ROLES, css_variables

__version__ = "0.5.0"

__all__ = [
    "ForgeApp",
    "MenuBar", "MenuDropdown", "accel", "underline_label",
    "ConfirmDialog", "ForgeModal", "ForgePanelScreen", "ShortcutsDialog", "LicenseDialog", "AboutDialog",
    "FORGE_CSS", "COLORS", "ROLES", "css_variables", "GPL3_NOTICE",
    "console_mode", "console_text", "glyph", "GLYPHS",
    "Notice", "notice_markup", "HintBar", "hints_markup", "ChangesBar", "SettingRow", "NumberPresets", "Toggle", "Choices", "CheckList",
    "FilterPicker", "ReviewDialog", "ChangeGroup", "review_markup", "ProgressDialog",
    "ManualScreen", "load_pages", "session_banner", "closing_notice", "runs_log_row",
    "__version__",
]
