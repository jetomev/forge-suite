# hypeForge — project rules

*How this project is built, tested and shipped. Written for the AI co-developer, and public on purpose: it is part of how the human + AI method is documented.*

## What it is
A [forgekit](https://github.com/jetomev/forgekit) (Python/Textual) terminal app that installs and manages the KognogOS Hyprland desktop on any Arch install. **Phase 0: there is no app code yet.**

## Non-negotiables (from docs/DECISIONS.md)
- **Hyprland settings are Lua only** (Hyprland 0.55+). Never write the retired `.conf` format for Hyprland itself.
- **Windows float by default**, and Win + arrows snap them, like Plasma.
- **One portable folder is the source of truth.** Nothing outside `$HOME` is ever edited by hand. System pieces are applied by the app, with a backup and an undo, through polkit and a fixed-purpose helper (grubForge's pattern). Never put a password field inside the terminal app.
- **Packages go through nog.** The Hyprland family is a nog group (D-9).
- **Must be readable on a plain text screen** (`TERM=linux`), which depends on forgekit#1.
- **Omarchy (MIT) is the reference.** Credit anything adapted from it and keep its notice.

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
`python3 scripts/make-banner.py` regenerates `assets/banner.svg` and `assets/snap-keys.svg`. Render them with `rsvg-convert` and look at the result before committing.
