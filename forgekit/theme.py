"""Catppuccin-Mocha palette, the colour roles, and the base forgekit stylesheet.

Apps set ``CSS = FORGE_CSS`` (and may append their own rules). Styling asks for a
*role* (``$forge-border``, ``$forge-muted``, ``$forge-accent``…), never a literal
colour, so it can resolve differently by mode (issue #1):

* in a terminal window, each role is a Catppuccin Mocha colour;
* on a plain text console (``TERM=linux``, see ``console.py``), each role is one
  of the console's own colours, chosen so the roles stay apart. Backgrounds use
  only the 8 basic colours, because bright backgrounds are not reliable there.

``ForgeApp.get_css_variables()`` supplies the right set. Apps can use the same
``$forge-*`` names in their own CSS and in markup (``[$forge-accent]…[/]``).
"""

from __future__ import annotations

# Catppuccin Mocha — https://catppuccin.com
COLORS = {
    "base": "#1e1e2e", "mantle": "#181825", "crust": "#11111b",
    "surface0": "#313244", "surface1": "#45475a", "surface2": "#585b70",
    "overlay0": "#7f849c", "subtext": "#a6adc8", "text": "#cdd6f4",
    "blue": "#89b4fa", "sapphire": "#74c7ec", "mauve": "#cba6f7",
    "green": "#a6e3a1", "yellow": "#f9e2af", "red": "#f38ba8",
    "boxblue": "#2b4a7a",
}

# role: (terminal window, text console)
ROLES: dict[str, tuple[str, str]] = {
    # the screen and its bars
    "bg":            (COLORS["base"],     "ansi_black"),
    "text":          (COLORS["text"],     "ansi_bright_white"),
    "muted":         (COLORS["subtext"],  "ansi_white"),
    "title-bg":      (COLORS["crust"],    "ansi_blue"),
    "title":         (COLORS["mauve"],    "ansi_bright_white"),
    "menubar-bg":    (COLORS["mantle"],   "ansi_black"),
    "hover":         (COLORS["blue"],     "ansi_bright_cyan"),
    "hover-bg":      (COLORS["surface0"], "ansi_black"),
    # blue, not cyan: the console shows underlined letters in cyan, and the
    # active item's underlined letter vanished on a cyan block (VM test)
    "active-bg":     (COLORS["boxblue"],  "ansi_blue"),
    "active":        (COLORS["text"],     "ansi_bright_white"),
    # panels, dialogs, dropdowns
    "surface":       (COLORS["surface0"], "ansi_black"),
    "raised":        (COLORS["surface1"], "ansi_blue"),
    "border":        (COLORS["surface2"], "ansi_white"),
    "field-border":  (COLORS["surface1"], "ansi_white"),
    "accent":        (COLORS["blue"],     "ansi_bright_cyan"),
    "title-accent":  (COLORS["mauve"],    "ansi_bright_magenta"),
    "warn":          (COLORS["yellow"],   "ansi_bright_yellow"),
    "danger":        (COLORS["red"],      "ansi_bright_red"),
    "ok":            (COLORS["green"],    "ansi_bright_green"),
    "selected-bg":   (COLORS["surface1"], "ansi_blue"),
    "selected":      (COLORS["blue"],     "ansi_bright_white"),
    # buttons: on the console a button is a coloured block with dark text
    "button-bg":     (COLORS["surface1"], "ansi_white"),
    "button":        (COLORS["text"],     "ansi_black"),
    "button-hover":  (COLORS["surface2"], "ansi_cyan"),
    "primary-bg":    (COLORS["boxblue"],  "ansi_cyan"),
    "primary":       (COLORS["text"],     "ansi_black"),
    "on-accent":     (COLORS["crust"],    "ansi_black"),
    "error-bg":      (COLORS["red"],      "ansi_red"),
    "on-error":      (COLORS["crust"],    "ansi_bright_white"),
    # scrollbars: a solid thumb on the console, no partial blocks
    "scroll-track":  (COLORS["surface0"], "ansi_black"),
    "scroll-thumb":  (COLORS["surface2"], "ansi_white"),
    "scroll-hover":  (COLORS["overlay0"], "ansi_white"),
    "scroll-drag":   (COLORS["blue"],     "ansi_cyan"),
}

# Things that are not colours but still differ by mode.
SHAPES: dict[str, tuple[str, str]] = {
    "round": ("round", "solid"),          # the console font has no rounded corners
    # no see-through shading on 16 colours: the screen behind shows unchanged
    "backdrop": ("black 45%", "transparent"),
    "dropdown-backdrop": ("black 30%", "transparent"),
    # the console draws bold as "bright", and bright black is dark grey, so
    # dark text on a coloured block must not be bold there
    "strong": ("bold", "none"),
}


def css_variables(console: bool) -> dict[str, str]:
    """The ``forge-*`` CSS variables for one mode."""
    i = 1 if console else 0
    out = {f"forge-{k}": v[i] for k, v in ROLES.items()}
    out.update({f"forge-{k}": v[i] for k, v in SHAPES.items()})
    return out


# The shell + dialog styling. Widget-scoped so apps only add their own section
# rules on top.
FORGE_CSS = """
Screen { background: $forge-bg; color: $forge-text; }

/* scrollbars — furniture, not content: gray family only, slim, accent only
   while dragging (scrollbar props don't inherit, hence the * selector) */
* {
    scrollbar-background: $forge-scroll-track;
    scrollbar-background-hover: $forge-scroll-track;
    scrollbar-background-active: $forge-scroll-track;
    scrollbar-color: $forge-scroll-thumb;
    scrollbar-color-hover: $forge-scroll-hover;
    scrollbar-color-active: $forge-scroll-drag;
    scrollbar-size-vertical: 1;
    scrollbar-size-horizontal: 1;
}

/* header: title bar (row 0) + menu bar (row 1) */
#forge-header { dock: top; height: 2; }
#forge-title {
    height: 1; background: $forge-title-bg; color: $forge-title;
    text-style: bold; text-align: center; content-align: center middle;
}
#forge-menubar { height: 1; background: $forge-menubar-bg; }
.menu-title { width: auto; height: 1; color: $forge-text; }
.menu-title:hover { background: $forge-hover-bg; color: $forge-hover; }
.menu-title.active { background: $forge-active-bg; color: $forge-active; text-style: $forge-strong; }

/* work area — no right padding so section scrollbars hug the screen edge */
#forge-work { padding: 1 0 1 2; height: 1fr; }

/* dropdown submenu */
MenuDropdown { align: left top; background: $forge-dropdown-backdrop; }
.forge-dropdown { background: $forge-surface; color: $forge-text; height: auto; border: $forge-round $forge-border; }
.forge-dropdown > .option-list--option-highlighted { background: $forge-selected-bg; color: $forge-selected; }

/* modals — panel scales with the terminal; buttons scroll with content.
   ForgeModal covers app-built dialogs so they center like the kit's own. */
ConfirmDialog, ForgePanelScreen, ForgeModal { align: center middle; background: $forge-backdrop; }
.forge-confirm { width: 50; height: auto; padding: 1 2; background: $forge-surface; border: $forge-round $forge-warn; }
.forge-confirm-msg { padding: 0 0 1 0; }
/* panels hug their content (F-7): short windows end a breath after the
   footer; long bodies cap at ~65% of the terminal height and scroll —
   the body carries the clamp (in vh) so the fixed footer always fits */
.forge-panel { width: 70%; height: auto; max-height: 100%; padding: 1 2; background: $forge-surface; border: $forge-round $forge-accent; }
.forge-panel-title { color: $forge-accent; text-style: bold; padding: 0 0 1 0; }
.forge-panel-body { height: auto; max-height: 65vh; }
/* F-8: fixed footer under a divider — buttons never scroll away.
   Kept thin (divider + button row; the panel's bottom padding is the
   air underneath). Definite height so layout reserves its rows. */
.forge-panel-footer { height: 2; padding: 0; border-top: solid $forge-border; }

/* form widgets (F-9, promoted from BitlaForge/alacrittyForge app CSS —
   every Forge app edits config, so forms are kit territory) */
Label { color: $forge-muted; padding: 1 0 0 0; }
Input { background: $forge-surface; color: $forge-text; border: solid $forge-field-border; }
Input:focus { border: solid $forge-accent; }
Select { background: $forge-surface; color: $forge-text; border: solid $forge-field-border; }
Select:focus { border: solid $forge-accent; }
/* console only (":ansi" = the app runs on basic colours): Select's inner box
   and Switch draw Textual's "tall" border from thin edge blocks the console
   font lacks, so there they get none / a plain line instead */
SelectCurrent:ansi { border: none; background: $forge-surface; color: $forge-text; }
Select:focus > SelectCurrent:ansi { border: none; }
Checkbox { background: $forge-bg; color: $forge-text; }
Switch.-on { color: $forge-accent; }
Switch:focus { border: tall $forge-accent; }
Switch:focus:ansi { border: solid $forge-accent; }
DataTable > .datatable--header { background: $forge-surface; color: $forge-accent; text-style: bold; }
DataTable > .datatable--cursor { background: $forge-selected-bg; color: $forge-text; }
/* compact one-row buttons — Textual's 3-row bordered default is too heavy */
.forge-buttons { height: auto; padding: 1 0 0 0; align-horizontal: right; }
.forge-buttons Button {
    height: 1; min-width: 10; border: none; padding: 0 2; margin: 0 0 0 2;
    background: $forge-button-bg; color: $forge-button; text-style: $forge-strong;
}
.forge-buttons Button:hover { background: $forge-button-hover; }
.forge-buttons Button:focus { background: $forge-primary-bg; color: $forge-primary; text-style: $forge-strong; }
.forge-buttons Button.-primary { background: $forge-primary-bg; color: $forge-primary; }
.forge-buttons Button.-primary:hover { background: $forge-accent; color: $forge-on-accent; }
.forge-buttons Button.-error { background: $forge-error-bg; color: $forge-on-error; }
.forge-buttons Button.-error:hover { background: $forge-warn; color: $forge-on-accent; }
"""
