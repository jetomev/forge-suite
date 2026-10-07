# forgekit v0.8.0 — Test Results (6 Oct 2026)

The release is one feature, the password's dots centred and sudoForge's box layout (forge-suite #34),
so the matrix is the feature's own: the field and the box checked by position on the line the screen
really draws, the password looked for on screen (it must never be there), every shipped app's own
suite run on this forgekit, a console preview, and Javier's look.

| Area | Result |
|---|---|
| Unit + headless tests | **104 PASS** (93 → 104, 0 warnings): dots counted and measured on the drawn line (centred within one cell, not at the left edge); the empty field's hint centred; Backspace, Ctrl+U, paste with a line break dropped, Backspace on empty; Enter and OK give the password and empty the field; Esc cancels and empties it; 120 characters all kept, the dots stay inside the border; `repr()` shows only the length; the dot is in the console font; the old layout reads the same with no heading; sudoForge's layout: heading, command, note, label centred, as wide as the field, top to bottom in order, a blank line before the label; the password never on screen |
| Found by the tests | The dots were drawn at the left: Textual does not apply a text's own centring inside a widget's `render()`. Now centred by hand. Also a test that looked for the field the instant the box was current, before its insides were built: the box now shrugs off being closed while it opens |
| Apps on 0.8.0 | nogForge 37 (types a password into the box end to end), grubForge 53, alacrittyForge 80, bitlaForge 64, displayForge 54: PASS |
| Console preview (`tools/console-preview.py`) | `examples/password.py` in both layouts with six characters typed: every character in the console font, every letter visible against its background — PASS. On a console the heading bar has no shade of its own (8 background colours); it stays readable |
| Javier, desktop | `examples/password.py` in a floating window on Sway: typing, centred dots, Backspace, Ctrl+U, Enter — *"perfect! great job!"* — **PASS** |
| Not run | A real text console (tty) on the VM. Belongs to sudoForge's own release check |
