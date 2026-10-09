# nightForge — section rules

*A Forge Suite app (D-60): the night light's settings app for hypeForge. Read the suite's `CLAUDE.md` first; this file adds what is particular here.*

- **One job: the night light** — on/off, evening warmth, when (sun at a place, or fixed times). Brightness stays displayForge's.
- **nightForge owns the night light** (proposed, question 8 of the design): at login hypeForge runs `nightforge start`, which reads `~/.config/nightforge/settings.toml` and starts wlsunset; saving restarts it. wlsunset has no settings file and no status: everything it needs is passed when it starts.
- **A design is approved by Javier, screen by screen, before code is written** (`docs/design/`, built by `build-drawings.py` + `build-page.py`, every drawing checked at 100 columns).
- **Built on forgekit, the displayForge / workspaceForge look;** keys from the menu (forgekit 0.10.0), buttons "Words (key)", quitting with unsaved changes asks; `--hypeforge` for hypeForge Settings.
- **Never leave the screens stuck:** a preview goes back by itself; stopping wlsunset puts the colours back.
- **Stop processes by their saved PID or exact name, never by command-line search.**
- **Where it runs, said everywhere** (README, GitHub, kognogos.org, AUR): hypeForge on Sway (wlroots); any terminal, a plain text console too; written for KognogOS.
- **The hidden bench** (hypeForge F-51 rule) before anything that starts or restarts processes at login goes live.
- Packages through nog; decisions in `docs/DECISIONS.md`; TODO.md after every step; plain words. Versioning: tags `nightforge-vX.Y.Z`, AUR `nightforge` after Javier's local test.
