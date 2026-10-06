# hypeForge — project rules

*How this project is built, tested and shipped. Written for the AI co-developer, and public on purpose: it is part of how the human + AI method is documented.*

## What it is
The KognogOS desktop on **Sway** (D-45): tiling, terminal apps first. Each feature is a small applet (`applets/`, D-47); every setting becomes its own Forge Suite app, held by **hypeForge Settings**, the control centre (D-59). **There is no installer app yet.**

## Non-negotiables (from docs/DECISIONS.md)
- **The three-part rule (D-57):** terminal apps first (1), Sway-compatible (2), smallest install (3). Nothing that brings KDE, GNOME or Hyprland pieces back (D-56): **KognogOS ships with Sway only.**
- **Every configurable thing is its own Forge app** on forgekit, with the same look; apps that connect read each other's settings files, never each other's code (D-59).
- **Any number of screens.** This desktop has three; hypeForge must work for one to six or more. Never hard-code three.
- **Packages go through nog.** Raw pacman/AUR only when strictly needed, and say why.
- **System pieces are applied by the app**, with a backup and an undo. Nothing outside `$HOME` is edited by hand.
- **The look is written down** (Javier, 2026-10-05): every change to colours, fonts, sizes, corners, shades or themes updates `docs/THEME.md` in the same commit — it is the Theme manager's blueprint.
- **Help moves with the desktop** (Javier, 2026-10-05): every new or changed feature updates its guide page in `applets/help/guide/` (and `pages.toml`) in the same commit — the key chart is checked by a script, the guide is not.
- **The key chart is checked on every commit** (`scripts/check-keys.py`, the pre-commit hook): a key added in `sway/config` must be in `applets/help/keys.toml`.
- **Must be readable on a plain text screen** (`TERM=linux`).
- **We learn from every project we use, and we never compare** . No "better than" or "unlike X" framing anywhere. Credit anything adapted and keep its notice.

## Documentation, at every step
- A new decision goes in `docs/DECISIONS.md`: newest first, numbered D-n, dated, with who decided.
- `TODO.md` is updated after every step, and `bash scripts/status.sh` must still parse it (`## Phase N · Name`, `- [ ]` / `- [x]`).
- Research goes in `docs/research/YYYY-MM-DD-<topic>.md`, with the commands run and the sources read.
- The README stays accurate top to bottom at every commit. Roadmap and changelog are newest first. The README keeps only upcoming work and the two most recent releases.
- Plain words throughout. The readers are not engineers.

## Release discipline
- Every phase ships as three steps: a `Phase N: <scope>` commit, then `docs: README + version bump for vX.Y.Z (Phase N complete)`, then an annotated, signed tag (`git tag -s -m`).
- Every commit carries a co-author trailer.
- Test matrices go in `testing/`, named `YYYYMMDD - Test Matrix for hypeForge vX-Y-Z.md`.
- Findings are numbered F-n and each gets an issue.
- The GitHub Release goes out before the AUR package.

## Assets
`assets/kognogos-emblem.png` (the bar's launcher button, the README), `assets/lock/` (the lock screen's blurred wallpaper). The new banner and social preview come with the public update, designed and approved first.
