# forgekit — changelog

*Newest first. The README's status box carries the two most recent versions; everything else is here.*

### 0.9.0 — October 7, 2026 · the menu bar wraps ([#40](https://github.com/jetomev/forge-suite/issues/40))

Found in hypeForge's Help & Keys on 2026-10-05, marked URGENT by Javier on 2026-10-07: the bar was
one line, so on a narrow window the sections at the right were cut off and could not be reached.
Every Forge app has the bar, so every Forge app had the bug.

- **`MenuBar`** lays its titles out in as many rows as the window needs, in order, and re-flows on
  every resize; a title wider than the whole window gets a row of its own. The header is
  `height: auto` so the work area moves down with it. Clicks, accelerator letters, dropdown
  anchoring and the active mark are unchanged (the mark survives a re-flow).
- Apps change nothing; they pick it up by depending on `python-forgekit>=0.9.0`.
- Tests: **110** (was 104): the row arithmetic, a seven-tab app at 40 columns (every title on
  screen, two rows, header grew), 100 columns (one row, as before), a click on a second-row title,
  the active mark after growing the window. Warnings: 0.

### 0.8.0 — October 6, 2026 · the password's dots centred ([#34](https://github.com/jetomev/forge-suite/issues/34))

Built for sudoForge, the password helper for the Sway desktop (its D-2): Javier wanted the typed
dots centred in the field, and Textual's `Input` cannot centre its text. *"Build it into forgekit"*,
so every Forge app's password box gets it.

- **`PasswordField`**: one dot per character, centred; nothing else is ever drawn. Backspace,
  Ctrl+U empties it, paste works (line breaks dropped, never sent). The password stays in memory
  only; `repr()` shows only its length. The dot comes from the glyph table, so a text console
  draws it too.
- **`PasswordDialog`** uses it, and takes `heading` (a bar saying who is asking), `detail` (the
  command, in the "changed" colour), `note` (a quieter line) and `label` ("Password for …"),
  all centred, with a blank line before the label. Without them the box reads as before.
- `examples/password.py` opens the box in sudoForge's layout (`plain` for the old one).
- Tests 93 → 104, warnings 0 → 0. Found by the tests before anyone saw it: the dots were drawn at
  the left (Textual does not apply a text's own centring there); now centred by hand.
- nogForge 37, grubForge 53, alacrittyForge 80, bitlaForge 64, displayForge 54 pass on it.

### 0.7.0 — October 6, 2026 · the shared start-up check ([#33](https://github.com/jetomev/forge-suite/issues/33))

Javier, the night displayForge 1.0.0 shipped: it must say clearly it works on Sway only, and check
at launch — if not Sway, say why, with only a Close button. No check existed in any Forge app; the
four shipped ones each check their own needs their own way (grubForge GRUB + polkit, nogForge
nog ≥ 1.7, bitlaForge minerd). This is the shared part; displayForge 1.0.1 is its first user, and
the shipped apps move onto it at their next versions.

- **`start_check(app_name, needs)`**: one call at the top of `main()`. All met: nothing shown.
  Something missing: one plain screen (Needs · Found · Why · Instead per need, "Nothing has been
  changed.", **Close (c)**; **Continue Anyway (a)** only when every missing need is optional), then
  the same words printed to the terminal as the run's record.
- **`Need` / `Finding` / `check_needs()`**, and the ready-made **`sway_session()`** (SWAYSOCK set and
  `swaymsg` answering; otherwise it names what is running — "KDE Plasma (Wayland)", "Hyprland
  (Wayland)", "a text console, no graphical session", "a terminal over SSH…"), **`program()`**
  (installed, and at least a version read from `--version`), **`service()`** (systemd unit active,
  user or system), **`a_file()`**. A check that raises counts as not met: the screen must appear.
- Button labels in Javier's format from the start: "Close (c)", "Continue Anyway (a)".
- `examples/needs.py`; console preview clean (every character in the console font, every letter
  visible).

Tests 67 → 93 (every check fed a known-bad input as well as a good one; the screen checked by
position: footer under the body, Continue left of Close). Warnings: 0 (was 0). Javier's run on the
desktop: PASS. The first release from the Forge Suite repository: the signed assets live under the tag
`forgekit-v0.7.0` there, and the AUR recipe (`462ecef`) fetches them from it.

### 0.6.0 — October 4, 2026 · a tool's run and its password, inside the app ([#6](https://github.com/jetomev/forgekit/issues/6))

Javier, about nogForge handing the terminal to nog: *"it is not beautiful, it is disrupting"*, and a
desktop password window *"doesn't make sense"* for a terminal app. He chose three of five researched
options (nogForge `docs/research/2026-10-04-nog-inside-the-ui.md`); this is the shared part.

- **`RunWindow` / `ForgeApp.run_in_app()`**: a program's steps (JSON lines in an events file) with a
  progress bar; its own screen folded until a question, a failure or F12; Yes/No for yes/no
  questions; menus like yay's typed in the screen; no question bar while an editor or pager runs.
- **`TerminalPane`**: a pseudo-terminal drawn with pyte, plus what pyte lacks: the alternate screen
  (an editor or pager gives the earlier output back) and a capped scrollback; a shrinking screen
  keeps its bottom; keys and Ctrl+C go to the program.
- **`PasswordBridge` / `PasswordDialog`**: sudo's password asked in the app (`SUDO_ASKPASS` → a
  helper → a 0700 folder, a 0600 socket, a one-time token); "try again" after a wrong one; closing
  the app never hangs on an open question.
- **`InAppPolkitAgent` / `ForgeApp.polkit_agent()`**: polkit's password asked in the app, for the
  app's own process (D-Bus AuthenticationAgent + PolkitAgent.Session). The PyGObject Listener route
  crashed (SIGSEGV) in the spike and is not used.
- Found on the way: `ReviewDialog` labels like "Install (i)" now answer to their key; the progress
  bar's half lines have console fallbacks (they showed "?"); `literal()` keeps outside text's
  brackets ("[N]one [A]ll" was eaten by markup).

Proven in the KognogOS VM on a real text console and by Javier on his desktop and tty3 (nogForge
and grubForge: *"works wonders"*). Tests 52 → 67. alacrittyForge 80, bitlaForge 64, grubForge 53,
nogForge 37 pass on it. New dependency: `pyte`; optional: `python-gobject` + `polkit`.

### 0.5.2 — October 3, 2026 · the bottom bar follows the screen shown
Coming back to a screen with nothing to select kept the last screen's keys in the bottom bar; found
by Javier in nogForge, present in every app. Tests 51 → 52.

### 0.5.1 — October 2, 2026 · number fields for alacrittyForge
`NumberPresets(decimals=True)` and fields as wide as their longest number, both found by
alacrittyForge 1.0. 51 tests.

*Earlier: 0.5.0 (forms and flows, for grubForge 2.0), 0.4.0–0.4.1 (console mode), 0.1–0.3: see the
[releases](https://github.com/jetomev/forgekit/releases) and the git history.*
