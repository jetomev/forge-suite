# forgekit — TODO

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

## Now · v0.4.0 · console mode (issue #1)

**The promise (Javier, 2026-10-01):** every Forge app is **readable and usable on a plain text console (`TERM=linux`)**. It does not have to look the same as in a terminal window.

**Measured on 2026-10-01** (desktop, Textual 8.2.8, console font `default8x16`, 256 glyphs):
- On `TERM=linux` Textual drops to the 16 basic colours ("standard") and maps each of forgekit's 16 Catppuccin shades to the nearest one, so greys and blues merge.
- The console font **cannot draw** the rounded corners `╭ ╮ ╰ ╯` that every forgekit panel, menu and dialog uses, nor `━ ┃ ▔ ▁ ▎ ▊` (scrollbars, heavy lines), nor `● ◉ ✓ ✗ ⚠ ⏳ ▸ … ⌨ ⚙` or any emoji.
- It **can** draw `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼`, `█ ▌ ▐ ░ ▒ ▓`, `○ •`, `▶ ▼ ▲ ◀ ►`, `· → ← ↑ ↓`.

Steps:
- [x] Project kit completed: `CLAUDE.md` and this `TODO.md` (Javier, 2026-10-01: mandatory for every project)
- [x] `python-pyte` installed through nog, for the console preview tool
- [ ] **Console preview tool** (`tools/console-preview.py`): run a command in a pseudo-terminal with `TERM=linux` at 80×25 / 100×30, feed the output to `pyte`, draw a PNG with the Linux console's 16-colour palette, mark every character the console font cannot draw in red, print a summary (colours used, undrawable characters). Baseline pictures of the v0.3.0 demo
- [ ] **Detection:** console mode when `TERM=linux`; `FORGE_ASCII=1` forces it on, `FORGE_ASCII=0` forces it off; exposed as `forgekit.CONSOLE` / `ForgeApp.console`
- [ ] **Semantic colour roles:** forgekit's CSS uses Textual variables (`$forge-border`, `$forge-muted`, `$forge-accent`, `$forge-danger`, `$forge-selected`, …) supplied by `ForgeApp.get_css_variables()`: Catppuccin in a terminal window, a hand-picked console colour per role in console mode, chosen so the roles stay distinguishable
- [ ] **Borders and scrollbars:** rounded corners become straight ones in console mode; scrollbars drawn with full blocks only
- [ ] **Glyph table** `forgekit.glyphs`: `ok`, `warn`, `error`, `busy`, `bullet`, `pointer`, … with console fallbacks (`✓`→`+`, `⚠`→`!`, `●`→`*`, `⏳`→`~`); the demo and the kit's own dialogs use it
- [ ] **Tests** (`tests/`, unittest + Pilot): detection and override, the variables in both modes, no undrawable character in the kit's own output in console mode, layout positions unchanged
- [ ] Console preview of the demo after the change; then **Javier on a real `tty3`**
- [ ] README (a "Text console" section, the promise, the override), version 0.4.0 in every surface, test matrix in `testing/`, release, AUR `python-forgekit` 0.4.0
- [ ] Close #1 with the full explanation; comment on grubforge#21, alacrittyforge#7, bitlaforge#2, nogforge#1 with how each app adopts it

## Next
- [ ] grubForge v2.0.0 moves onto forgekit, inheriting console mode (grubforge#21)
- [ ] alacrittyForge and bitlaForge move their own colours and glyphs to the roles and the glyph table (alacrittyforge#7, bitlaforge#2)
- [ ] Promotion candidates from alacrittyForge: `FilterPickerModal` (type-to-filter long lists) and ListView styling

## Open questions
- [ ] Does forgekit's README need its own roadmap and changelog sections (the other repos have them; forgekit has only the Releases page)?

## Done (most recent releases; full history on the Releases page)
- [x] v0.3.0 (2026-08-10): form widgets into the kit; declarative close keys on panels (`CLOSE_KEYS`)
- [x] v0.2.1 (2026-08-09): panel anatomy: auto-sized shortcut keys, panels that hug their content, a fixed footer
