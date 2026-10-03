# forgekit — TODO

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

## Done · v0.5.1 · number fields for alacrittyForge · released 2026-10-02

- [x] `NumberPresets(decimals=True)` (`66874fe`) and the field as wide as its longest number (`c8967b2`); the example app named bitlaForge (`3b647ec`). 51 tests, 0 warnings. Released before alacrittyForge 1.0, which needs it.

## Done · v0.5.0 · forms and flows, built with grubForge 2.0 · released 2026-10-02

- [x] Settings pieces: SettingRow (changed mark on its own line), Toggle, Choices, CheckList, NumberPresets, FilterPicker, ChangesBar, HintBar, Notice
- [x] Flows: ReviewDialog/ChangeGroup, ProgressDialog, ConfirmDialog(default_no), ManualScreen, session banner / closing note / runs log
- [x] Fits at 100 columns (`dcafa19`); 48 tests, 0 warnings; `testing/20261002 - Test Results for forgekit v0-5-0.md`
- [x] README (Forms and flows, gallery picture), version 0.5.0 everywhere
- [x] Released: signed tag, signed archive + checksums, GitHub release, AUR `python-forgekit` 0.5.0-1 (before grubForge 2.0, which needs it)

## Next

- [ ] alacrittyForge and bitlaForge onto the 0.5.0 pieces (one design language across the suite)

## Done · v0.4.0 + v0.4.1 · console mode (issue #1) · released 2026-10-01

**The promise (Javier, 2026-10-01):** every Forge app is **readable and usable on a plain text console (`TERM=linux`)**. It does not have to look the same as in a terminal window.

**Measured on 2026-10-01** (desktop, Textual 8.2.8, console font `default8x16`, 256 glyphs):
- On `TERM=linux` Textual drops to the 16 basic colours ("standard") and maps each of forgekit's 16 Catppuccin shades to the nearest one, so greys and blues merge.
- The console font **cannot draw** the rounded corners `╭ ╮ ╰ ╯` that every forgekit panel, menu and dialog uses, nor `━ ┃ ▔ ▁ ▎ ▊` (scrollbars, heavy lines), nor `● ◉ ✓ ✗ ⚠ ⏳ ▸ … ⌨ ⚙` or any emoji.
- It **can** draw `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼`, `█ ▌ ▐ ░ ▒ ▓`, `○ •`, `▶ ▼ ▲ ◀ ►`, `· → ← ↑ ↓`.

Steps:
- [x] Project kit completed: `CLAUDE.md` and this `TODO.md` (Javier, 2026-10-01: mandatory for every project)
- [x] `python-pyte` installed through nog, for the console preview tool
- [x] **Console preview tool** (`tools/console-preview.py`): run a command in a pseudo-terminal with `TERM=linux` at 80×25 / 100×30, feed the output to `pyte`, draw a PNG with the Linux console's 16-colour palette, mark every character the console font cannot draw in red, print a summary (colours used, undrawable characters). Baseline pictures of the v0.3.0 demo · **done:** baseline showed black-on-black bars, rounded corners and thick edge blocks the font lacks, input frames invisible, `⛏ —` undrawable (`docs/console/v0.3.0-on-a-text-console.png`)
- [x] **Detection:** console mode when `TERM=linux`; `FORGE_ASCII=1` forces it on, `FORGE_ASCII=0` forces it off; exposed as `forgekit.console_mode()` / `ForgeApp.forge_console` · **done** (a bug found on the way: Textual's App already has `console`, so the flag lives in `forge_console`; a test guards it)
- [x] **Semantic colour roles:** forgekit's CSS uses Textual variables (`$forge-border`, `$forge-muted`, `$forge-accent`, `$forge-danger`, `$forge-selected`, …) supplied by `ForgeApp.get_css_variables()`: Catppuccin in a terminal window, a hand-picked console colour per role in console mode, chosen so the roles stay distinguishable · **done:** 33 roles in `theme.py` (`ROLES`) + `SHAPES`; console backgrounds only the 8 basic colours; no bold on coloured blocks there (the console shows bold as bright, so black turned grey); see-through backdrops become transparent. **Window mode unchanged:** the four README screenshots regenerate identical to v0.3.0
- [x] **Borders and scrollbars:** rounded corners become straight ones in console mode; scrollbars drawn with full blocks only · **done** (`$forge-round`; Select/Switch thin "tall" edges only under `:ansi`; `ConsoleScrollBarRender`)
- [x] **Glyph table** `forgekit.glyphs`: `ok`, `warn`, `error`, `busy`, `bullet`, `pointer`, … with console fallbacks (`✓`→`+`, `⚠`→`!`, `●`→`*`, `⏳`→`~`); the demo and the kit's own dialogs use it · **done:** `glyph()` + `GLYPHS` in `console.py`, plus `ConsoleGlyphFilter`, which swaps every character outside the font's 185 + ASCII (read from `default8x16`) at output, same width; accents fall back to the letter (Á → A)
- [x] **Tests** (`tests/`, unittest + Pilot): detection and override, the variables in both modes, no undrawable character in the kit's own output in console mode, layout positions unchanged · **done: 22 tests, all green;** checked in the failing direction (the naming bug and a disabled swap each make tests fail)
- [x] Console preview of the demo after the change: every view (main, menu, edit, About via F1) draws only console characters (`docs/console/v0.4.0-on-a-text-console.png`)
- [x] **F-10: Help cannot be opened from the keyboard on a text console** (it sends Ctrl+H as the Backspace byte, `\x08`, and Textual reads that as Backspace) · **fixed:** F1 opens Help too (the console sends `ESC [[A`, which Textual reads as F1); tested in both modes
- [x] **Real console test on the KognogOS VM** (Javier's choice, 2026-10-01: *"can we test this on a vm instead?"*): `kognog-hypeforge`, snapshot first, demo on tty3 through the guest agent, keys with `virsh send-key`, screen read from `/dev/vcsa3` and redrawn with `tools/vcsa-shot.py`; VM reverted afterwards. **Passed:** menus, edit window, F1 → Help (F-10 proven on a real console), About, no stray characters
- [x] **F-11 (found by the VM test): the console shows underline as cyan and italic as green.** The active menu item's underlined letter vanished on its cyan block ("ashboard", "onfig"); the About tagline turned green · **fixed:** active item on blue, no italic in console mode; `console-preview.py` now models both and fails on any letter drawn in its own background colour (checked against the old colours: it flags the "D"); re-run on the VM: "Dashboard" whole, tagline grey · 23 tests
- [x] README: "On a plain text console" section (the promise, before/after pictures, the override, the tools), F1 in the keyboard model, new objects in "What's in the box"; version 0.4.0 in `pyproject.toml`, `__init__.py`, README
- [x] `testing/20261001 - Test Matrix / Test Results for forgekit v0-4-0.md`: 23 tests, 0 warnings, screenshots identical, AUR smoke in both modes, real console on the VM
- [x] Findings as issues: F-10 #2, F-11 #3 (opened and closed)
- [x] **Released 2026-10-01:** signed tag `v0.4.0` (`133b835`), signed archive + checksums on GitHub, marked Latest (download matches byte for byte); AUR `python-forgekit` 0.4.0-1 pushed (`656bc2c`): checksum, signature and `.SRCINFO` pre-flight passed, `makepkg` built with the check passing in both modes
- [x] bitlaForge 0.2.1 and alacrittyForge 0.2.0 (as installed) checked on forgekit 0.4.0 without any change of theirs: both start in both modes, and the console preview finds no undrawable character and no invisible letter
- [x] Installed on the desktop by Javier with `nog install python-forgekit` (nog rightly refuses AUR builds with nobody at the keyboard): `python-forgekit 0.4.0-1`; bitlaForge and alacrittyForge start on it in both modes. (The AUR's info service lagged ~15 min after the push while its web page and repository already showed 0.4.0)
- [x] #1 closed with the full explanation; grubforge#21, alacrittyforge#7, bitlaforge#2, nogforge#1 told what they get by upgrading and what is theirs to do

## Now · v0.5.0 — the pieces grubForge v2.0.0 needs (2 Oct 2026, not released yet)
Design approved by Javier: grubforge `docs/design/v2.0.0-screens.html`. Proven in grubForge before release (*"a library proves its API through apps"*).
- [x] Roles `changed` (peach / console magenta), `info`, `hint-bg`, `hint-key`; glyphs changed, new, fixed, info, default, down, check-on, radio-on
- [x] `Notice` (designed message, one blank line around), `HintBar` (keys follow focus via `FORGE_HINTS`), `ChangesBar`, `SettingRow`, `NumberPresets` (one Tab stop, ↑↓ presets), `Toggle` ("● On / ○ Off" in words), `Choices` ("( ) / (•)" row, ←→)
- [x] `FilterPicker` (promoted from alacrittyForge: current marked + highlighted, count, typed value), `ReviewDialog` (old → new), `ProgressDialog`, `ManualScreen` (+ `load_pages`)
- [x] `closing.py`: `session_banner`, `closing_notice`, `runs_log_row` — the start and end printed in the terminal (Javier's rule from nog)
- [x] Shell, opt-in: `SHOW_HINT_BAR`, `SHOW_CHANGES_BAR`, `set_title_status`, `before_quit`
- [x] Styles: one-border Select; fields as outlines in forms; lists, checklists, text areas, toasts, the manual
- [x] `examples/gallery.py`; tests 26 → 48, incl. the gallery on a real console preview; alacrittyForge and bitlaForge still mount and switch sections
- Found while building: a method named `log` hid Textual's own (crash on focus); the filter field selected its first letter (lost when typing on the list); the SVG→PNG converter collapsed spaces (screens are now checked through Chrome)
- [ ] Release after grubForge v2.0.0 proves it; README + docs + AUR then

## Next
- [x] Installed on the desktop by Javier through nog: `python-forgekit 0.4.1-1`; bitlaForge and alacrittyForge start on it, "Help F1" in console mode only. (First try reinstalled 0.4.0: the AUR info service lagged right after the push and yay reused its cached build; the second run got 0.4.1)
- [x] Decided (Javier, 2026-10-01): in a normal terminal the focus colour stays as it is (primary and focused share `#2B4A7A`, bold tells them apart): *"focus color, as is it's ok."*
- [x] **Javier tested console mode himself in the apps we already ship** (bitlaForge 0.2.1, alacrittyForge 0.2.0), in the KognogOS VM on 2026-10-01, after Claude's own run of the same matrix there. Found **F-12 #4** (nothing shows Help is on F1) and **F-13 #5** (Tab focus not visible on a console): both fixed, re-tested by Javier (*"all tested and good!"*), shipped as **v0.4.1**: GitHub Latest (signed), AUR `b889e67`, #4 and #5 closed, the VM reverted to its snapshot. Also from his run: KognogOS #8 (greetForge on tty), bitlaforge#3 (Esc stays in the field). K-1 not reproduced on a real console
- [ ] grubForge v2.0.0 moves onto forgekit, inheriting console mode (grubforge#21) — **after the test above**
- [ ] alacrittyForge and bitlaForge move their own colours and glyphs to the roles and the glyph table (alacrittyforge#7, bitlaforge#2)
- [ ] Promotion candidates from alacrittyForge: `FilterPickerModal` (type-to-filter long lists) and ListView styling

## Open questions
- [ ] Does forgekit's README need its own roadmap and changelog sections (the other repos have them; forgekit has only the Releases page)?

## Done (most recent releases; full history on the Releases page)
- [x] v0.3.0 (2026-08-10): form widgets into the kit; declarative close keys on panels (`CLOSE_KEYS`)
- [x] v0.2.1 (2026-08-09): panel anatomy: auto-sized shortcut keys, panels that hug their content, a fixed footer
