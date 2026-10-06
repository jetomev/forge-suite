# Forge Suite — the list

**Target: the first KognogOS release (v1.0, April 2027).** Each section keeps its own detailed list; this one tracks the suite. Updated after every step.

## The move-in (D-60, phased)
- [x] `jetomev/hypeforge` renamed `jetomev/forge-suite` (old links redirect); hypeForge moved into `hypeforge/` (2026-10-05)
- [x] GitHub About + topics for the suite (2026-10-06)
- [x] kognogos.org: "KognogOS = nog + the Forge Suite", hypeForge on Sway with the new banner, displayForge 1.0, forgekit's new home, 6 on the AUR — live 2026-10-06 (homelab `a9fdc2e`)
- [x] **forgekit moved in** (2026-10-06): full history, tags `forgekit-v0.1.0…v0.6.0`, old repo archived with a pointer, `~/Programs/forgekit` → shortcut. At its next release the AUR recipe points here
- [ ] alacrittyForge · bitlaForge · nogForge move in, one at a time, each tested; AUR recipes repointed
- [ ] grubForge moves in last (most users, outside contributors)
- [ ] Release rules (`~/.claude/rules/release.md`) adapted for per-app tags in one repository

## Ideas
- [ ] **Desktop entries in every Forge app's package** (2026-10-06): none of the four AUR apps ships one — grubforge#37, alacrittyforge#18, bitlaforge#12, nogforge#16; hypeForge carries its own until then
- [ ] **fileForge** (Javier, 2026-10-06) — our own file manager, **later**: forgekit look, **full mouse support** (what superfile lacks for him), keyboard too. Replaces the mcForge question below.
- [ ] **mcForge?** (Javier, 2026-10-06) — Midnight Commander is free software (GPLv3, written in C, github.com/MidnightCommander/mc), so a fork is allowed, and GPLv3 matches ours. Honest size: ~300,000 lines of C, 30 years old — a fork means maintaining all of it. Lighter path that fits D-59: an **mcForge settings app** (look, editor, panels, keys) over the stock mc. Decide later.

## Sections
- **displayForge** — **1.0.0 released 2026-10-06**; next: the 1.0.x tests → [displayforge/TODO.md](displayforge/TODO.md)
- **forgekit** — 0.6.0; next: button labels "Words (k)" → [forgekit/TODO.md](forgekit/TODO.md)
- **hypeForge** — the bar, launcher (with a Forge Suite section), sound / network / Bluetooth / USB done; next: password helper, printing, night light → [hypeforge/TODO.md](hypeforge/TODO.md)
