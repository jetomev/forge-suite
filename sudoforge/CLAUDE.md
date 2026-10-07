# sudoForge — project rules

*The password helper for the Sway desktop, as a Forge Suite app. Section of the Forge Suite repository (D-60); read the suite's `CLAUDE.md` too. Born from hypeForge D-56 / D-61.*

## What it is
One floating box for every admin request in a Sway session: polkit's admin pop-up (a **session-wide authentication agent**) and `sudo -A` (an **askpass helper**). A background service with no window; the box (forgekit's `PasswordDialog`, sudoForge's layout, D-2) opens in its own small Alacritty window only when asked.

## Non-negotiables
- **The password is never written anywhere** — not to disk, a command line, a log, an argument or an environment variable. It travels only over private sockets (a `0700` folder in `$XDG_RUNTIME_DIR`, peer uid checked) and is printed once, to sudo. Tests look for it in every log and on screen.
- **sudoForge never gets admin rights and never decides if a password is right.** polkit's own setuid helper checks it (`PolkitAgent.Session`); sudo checks its own.
- **One box at a time.** A second request waits for the first.
- **Fail closed, in plain words.** No service, no Sway, a box that dies: the request is cancelled and sudo/polkit say "no password". Never hang, never guess.
- **System files only through the app, with a backup and an undo** (`/etc/sudo.conf`, D-3), and only through polkit itself.
- **Terminals keep asking in the terminal** (D-4): only `sudo -A`, nog with `NOG_ASKPASS=1`, and polkit come here.
- Built on forgekit; colours only through its roles; readable on a text console.

## How to run and test
- Tests: `python -m unittest discover -s tests -v` from this folder (stand-in boxes and sudo prompts; nothing asks the real system unless a test says so).
- The service by hand: `python main.py service` (Ctrl+C stops it and gives polkit back). Its record: `~/.local/state/sudoforge/service.log`.
- Decisions in `docs/DECISIONS.md` (D-n); `TODO.md` after every step; plain words. Releases: tag `sudoforge-vX.Y.Z`.
