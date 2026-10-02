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
    "peach": "#fab387",
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
    # v0.5.0: a value changed but not saved yet (peach; magenta on the console,
    # where yellow is already "warn") and plain information (blue)
    "changed":       (COLORS["peach"],    "ansi_bright_magenta"),
    "info":          (COLORS["blue"],     "ansi_bright_cyan"),
    # v0.5.0: the hint bar — keys in the accent colour, words muted
    "hint-bg":       (COLORS["crust"],    "ansi_black"),
    "hint-key":      (COLORS["blue"],     "ansi_bright_cyan"),
    "selected-bg":   (COLORS["surface1"], "ansi_blue"),
    "selected":      (COLORS["blue"],     "ansi_bright_white"),
    # buttons: on the console a button is a coloured block with dark text
    "button-bg":     (COLORS["surface1"], "ansi_white"),
    "button":        (COLORS["text"],     "ansi_black"),
    "button-hover":  (COLORS["surface2"], "ansi_cyan"),
    "primary-bg":    (COLORS["boxblue"],  "ansi_cyan"),
    # F-13: on the console, focus needs a colour no other button state uses
    # (Textual marks focus with a tint + bold, which a console cannot show)
    "focus-bg":      (COLORS["boxblue"],  "ansi_blue"),
    "focus":         (COLORS["text"],     "ansi_bright_white"),
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
/* v0.5.0: one border, on the visible box — Select's outer frame drew a
   second one around it (five rows for one value) */
Select { background: $forge-bg; border: none; height: 3; }
Select > SelectCurrent { background: $forge-surface; color: $forge-text; border: solid $forge-field-border; }
Select:focus > SelectCurrent { border: solid $forge-accent; }
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

/* F-13, console only: every button, in the kit's bar or the app's own rows.
   normal = grey, primary = cyan, error = red, FOCUSED = blue with bright white
   (a colour no other state uses), so focus visibly moves on Tab */
Button:ansi { background: $forge-button-bg; color: $forge-button; text-style: none; }
Button.-primary:ansi { background: $forge-primary-bg; color: $forge-primary; }
Button.-error:ansi { background: $forge-error-bg; color: $forge-on-error; }
Button:hover:ansi { background: $forge-button-hover; }
Button:focus:ansi, .forge-buttons Button:focus:ansi { background: $forge-focus-bg; color: $forge-focus; text-style: none; }

/* ── v0.5.0 ─────────────────────────────────────────────────────────────── */

/* bottom bars: changes (unsaved work + its buttons) over hints (keys) */
#forge-footer { dock: bottom; height: auto; }
#forge-changes { height: 1; background: $forge-menubar-bg; }
#forge-changes-msg { width: 1fr; height: 1; }
#forge-changes-actions { width: auto; height: 1; padding: 0 1 0 0; }
#forge-hints { height: 1; background: $forge-hint-bg; color: $forge-muted; }

/* the designed notice: exactly one blank line before and after */
.forge-notice { height: auto; margin: 1 0; }

/* a setting in a form: label, control, changed mark; a muted line under it */
.forge-setting { height: auto; margin: 0 0 1 0; }
.forge-setting-line { height: auto; }
.forge-setting-label { width: 26; height: 3; content-align: left middle; color: $forge-text; }
.forge-setting-line > Select { width: 48; }
.forge-setting-line > Input { width: 48; }
.forge-setting-line > Switch { width: auto; }
.forge-setting-mark { width: auto; min-width: 12; height: 3; padding: 0 0 0 2; content-align: left middle; }
.forge-setting-note { height: auto; padding: 0 0 0 26; }
/* fields in a form are outlines on the screen's own background: one colour
   inside and out, the border carries the shape (and the focus) */
.forge-setting Input, .forge-setting .forge-toggle, .forge-setting Select,
.forge-setting SelectCurrent, .forge-setting SelectionList, .forge-setting .forge-choices,
.forge-setting .forge-number { background: $forge-bg; background-tint: transparent 0%; }
.forge-setting Input:focus { background: $forge-bg; background-tint: transparent 0%; }
.forge-setting SelectionList > .option-list--option { background: $forge-bg; }

/* a number with preset buttons */
.forge-number { height: 3; width: auto; }
.forge-number-input { width: 9; }
.forge-number-unit { width: auto; height: 3; padding: 0 2 0 1; content-align: left middle; color: $forge-muted; }
.forge-preset {
    height: 1; min-width: 3; margin: 1 0 0 1; padding: 0 1; border: none;
    background: $forge-button-bg; color: $forge-button; text-style: none;
}
.forge-preset:hover { background: $forge-button-hover; }
.forge-preset.-selected { background: $forge-selected-bg; color: $forge-selected; text-style: $forge-strong; }
.forge-preset:focus { background: $forge-focus-bg; color: $forge-focus; }

/* v0.5.0 controls that say their state in words */
.forge-toggle { width: auto; height: 3; border: solid $forge-field-border; background: $forge-surface; color: $forge-text; padding: 0 1; }
.forge-toggle:focus { border: solid $forge-accent; }
.forge-choices { width: auto; height: 3; border: solid $forge-field-border; background: $forge-bg; color: $forge-text; }
.forge-choices:focus { border: solid $forge-accent; }

/* choice widgets, both modes */
Input.-invalid { border: solid $forge-danger; }
Input.-invalid:focus { border: solid $forge-danger; }
RadioSet { layout: horizontal; height: auto; width: auto; background: $forge-bg; border: solid $forge-field-border; padding: 0 1; }
RadioSet:focus { border: solid $forge-accent; }
RadioButton { background: $forge-bg; color: $forge-text; padding: 0 2 0 0; }
SelectionList { background: $forge-surface; color: $forge-text; border: solid $forge-field-border; height: auto; max-height: 14; }
SelectionList:focus { border: solid $forge-accent; }
SelectionList > .option-list--option-highlighted { background: $forge-selected-bg; color: $forge-selected; }
/* an unticked box is empty: the faint X read as "ticked" */
SelectionList > .selection-list--button { color: $forge-surface; background: $forge-surface; }
SelectionList > .selection-list--button-highlighted { color: $forge-selected-bg; background: $forge-surface; }
SelectionList > .selection-list--button-selected { color: $forge-ok; background: $forge-surface; text-style: bold; }
SelectionList > .selection-list--button-selected-highlighted { color: $forge-ok; background: $forge-surface; text-style: bold; }
OptionList { background: $forge-surface; color: $forge-text; border: solid $forge-field-border; }
OptionList:focus { border: solid $forge-accent; }
OptionList > .option-list--option-highlighted { background: $forge-selected-bg; color: $forge-selected; text-style: $forge-strong; }
SelectOverlay { background: $forge-surface; color: $forge-text; border: solid $forge-accent; }
SelectOverlay > .option-list--option-highlighted { background: $forge-selected-bg; color: $forge-selected; }
ListView { background: $forge-bg; border: solid $forge-field-border; }
ListView:focus { border: solid $forge-accent; }
ListItem { background: $forge-bg; color: $forge-text; }
ListView > ListItem.-highlight { background: $forge-selected-bg; color: $forge-selected; }
TextArea { background: $forge-surface; color: $forge-text; border: solid $forge-field-border; }
TextArea:focus { border: solid $forge-accent; }
Toast { background: $forge-surface; color: $forge-text; }
Toast.-information { border-left: outer $forge-info; }
Toast.-warning { border-left: outer $forge-warn; }
Toast.-error { border-left: outer $forge-danger; }

/* floating windows */
.forge-picker { width: 64; }
#picker-list { height: auto; max-height: 16; }
#picker-count { height: 1; padding: 0 0 0 1; }
.forge-picker-hint { padding: 0 0 1 0; }
.forge-review { width: 84; }
.forge-progress { width: 64; }
#progress-log { padding: 1 0 0 0; }

/* the manual */
ManualScreen { background: $forge-bg; }
#forge-manual { height: 1fr; }
#forge-manual-title { height: 1; background: $forge-title-bg; color: $forge-title; text-style: bold; }
#forge-manual-body { height: 1fr; }
#forge-manual-contents { width: 32; height: 1fr; border: none; border-right: solid $forge-border; background: $forge-bg; padding: 1 1 0 1; }
#forge-manual-page { width: 1fr; height: 1fr; padding: 0 2; }
#forge-manual-md { background: $forge-bg; }
#forge-manual-md MarkdownH1 { color: $forge-title-accent; text-style: bold; background: $forge-bg; border: none; content-align: left top; }
#forge-manual-md MarkdownH2 { color: $forge-accent; text-style: bold; background: $forge-bg; border: none; }
#forge-manual-md MarkdownH3 { color: $forge-text; text-style: bold; background: $forge-bg; }
#forge-manual-md MarkdownFence { background: $forge-surface; }
"""
