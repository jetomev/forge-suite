# sudoForge — changelog

*Newest first.*

### 1.0.0 — not released yet · one password box for every admin request ([#35](https://github.com/jetomev/forge-suite/issues/35))

- **The service** (`sudoforge service`): a polkit agent for the whole login session plus a private door for `sudo -A`; one box at a time; a cancelled request closes its box; a record in `~/.local/state/sudoforge/service.log` that never holds a password.
- **The sudo helper** (`sudoforge-askpass`): what sudo runs for `sudo -A`; only sudo itself may ask; no service → plain words and sudo stops.
- **The box**: forgekit 0.8.0's password box in sudoForge's approved layout (D-2), floating and centred on the screen in use, saying who is asking and what for.
- **`setup` / `undo` / `status`** for `/etc/sudo.conf` (D-3): two marked lines, a backup first, asked through the box itself.
- **hypeForge**: started at login, its window floats, a Help page ("Passwords", Tools tab).
- **F-1** ([#36](https://github.com/jetomev/forge-suite/issues/36)): the box crashed on start in the first live test (forgekit's colours were not loaded); fixed, and the real box is now tested.
- Tests: 36 + a live polkit check. Warnings: 0.
