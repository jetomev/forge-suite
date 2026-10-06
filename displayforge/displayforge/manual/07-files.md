# Where things are kept

| What | Where |
|---|---|
| Your saved screens | `~/.config/sway/outputs` — Sway reads it at every login |
| Backups (the last 20) | `~/.config/displayforge/backups/` |
| Names and which control is which screen | `~/.config/displayforge/screens.toml` |

**Safety:** every change you try comes with a countdown that goes back by itself — and that countdown runs on its own, outside displayForge, so the screens come back even if displayForge closes. Saving writes the whole file at once (never half), with a backup of the old one first.

displayForge is part of the **Forge Suite** for KognogOS. Made by jetomev (Javier) with Claude (Anthropic). Free software, GPLv3.
