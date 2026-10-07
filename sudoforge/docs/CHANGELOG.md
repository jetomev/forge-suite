# sudoForge — changelog

*Newest first.*

### 1.0.1 — October 7, 2026 · the first backup is kept ([#37](https://github.com/jetomev/forge-suite/issues/37))

- **F-2:** a second `sudoforge setup` (for example after moving from the source checkout to the installed package) overwrote `/etc/sudo.conf.sudoforge-backup` with a file that already held sudoForge's two lines. Now the backup is taken only when there is none yet, or when the file carries no sudoForge mark — so it is always the file from before sudoForge touched it. Nothing was ever lost: `sudoforge undo` removes only our two lines, and never reads the backup.
- Two new tests: a second setup with another helper path leaves the backup as the original; a setup after an undo backs up the file as it is then.
- Tests: 38 (was 36). Warnings: 0.

### 1.0.0 — October 6, 2026 · one password box for every admin request ([#35](https://github.com/jetomev/forge-suite/issues/35))

- **The service** (`sudoforge service`): a polkit agent for the whole login session plus a private door for `sudo -A`; one box at a time; a cancelled request closes its box; a record in `~/.local/state/sudoforge/service.log` that never holds a password.
- **The sudo helper** (`sudoforge-askpass`): what sudo runs for `sudo -A`; only sudo itself may ask; no service → plain words and sudo stops.
- **The box**: forgekit 0.8.0's password box in sudoForge's approved layout (D-2), floating and centred on the screen in use, saying who is asking and what for.
- **`setup` / `undo` / `status`** for `/etc/sudo.conf` (D-3): two marked lines, a backup first, asked through the box itself.
- **hypeForge**: started at login, its window floats, a Help page ("Passwords", Tools tab).
- **F-1** ([#36](https://github.com/jetomev/forge-suite/issues/36)): the box crashed on start in the first live test (forgekit's colours were not loaded); fixed, and the real box is now tested.
- Tests: 36 + a live polkit check (skips itself when the real service already holds the session: polkit allows one agent per session). Warnings: 0.
- Javier's run, the full matrix: printer unlock and cancel, undo/setup twice, a reboot with the service starting by itself, two requests at once — *"All work perfect!"*
