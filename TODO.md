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
- **sudoForge** — **1.0.1 released and installed 2026-10-07** (F-2 #37 closed: the first backup of `/etc/sudo.conf` is kept, this desktop's backup repaired; 38 tests), after 1.0.0 on 2026-10-06 (AUR `sudoforge`; closes hypeForge F-42/F-44); next: a sudoForge pinentry and the keyring → [sudoforge/TODO.md](sudoforge/TODO.md)
- **displayForge** — **1.0.1 released 2026-10-06** (Sway only, checked at launch); next: the 1.0.x tests, the KDE-login check → [displayforge/TODO.md](displayforge/TODO.md)
- **forgekit** — **0.8.0 released 2026-10-06** (the password's dots centred, #34; 0.7.0 the start-up check); next: button labels "Words (k)", fold sudoForge's session agent back in → [forgekit/TODO.md](forgekit/TODO.md)
- **hypeForge** — the bar, launcher, sound / network / Bluetooth / USB done; the password pop-up done (sudoForge); next: printing, night light → [hypeforge/TODO.md](hypeforge/TODO.md)
- [x] **Every surface shows live versions** (Javier, 2026-10-06): kognogos.org (rebuilt in the homelab repo — it had been server-only and was wiped by a deploy), and live badges in the KognogOS, suite and hypeForge READMEs; kognogos.org "Honest progress" brought current

## 2026-10-07 — the issue sweep
- [x] **17 open issues → 5** (Javier: "close them all tonight"). Closed with a full explanation each: #33 and #32 had shipped (forgekit 0.7.0, displayForge 1.0.1) and were left open by oversight; #17 #16 #15 #9 #13 #5 #7 #4 described the Hyprland days, cleared off this computer on 10-05; #8 holds by construction (every app is on forgekit ≥ 0.4); #22 (D-44) is carried out, Phase 10 complete. Left open: #37 (sudoForge 1.0.1, tonight), #25 (F-43, fix prepared, Javier's test), #19 (default apps, a pick for Javier), #23 (F-41, Javier deferred it 10-04), #10 (the Plasma marker, by rule)
- [ ] Found on the way: `monique` 0.8.3 (the Hyprland screens app) is still installed and unused — **Javier (10-07): remove it**; nog from Claude's shell could not (no terminal to answer pacman's question → jetomev/nog#48), Javier runs it in a terminal

## 2026-10-06 evening — the first releases from the suite
- [x] **forgekit 0.7.0** (`forgekit-v0.7.0`, GitHub Release with signed assets, AUR `python-forgekit` fetching from this repository) and **displayForge 1.0.1** (`displayforge-v1.0.1`, Latest): the per-app tag release works end to end. Details in each section's TODO
- [ ] Write the per-app release recipe (archive a section at its tag, sign, Release, AUR) into `forgekit/CLAUDE.md` and this file, now that it is proven
