# forgekit — changelog

*Newest first. The README's status box carries the two most recent versions; everything else is here.*

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
