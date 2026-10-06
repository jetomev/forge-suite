# forgekit — changelog

*Newest first. The README's status box carries the two most recent versions; everything else is here.*

### 0.7.0 — on `main` since October 6, 2026, release pending Javier's run · the shared start-up check ([#33](https://github.com/jetomev/forge-suite/issues/33))

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

Tests 67 → 92 (every check fed a known-bad input as well as a good one; the screen checked by
position: footer under the body, Continue left of Close). Warnings: 0 (was 0).

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
