# forgekit — project rules

*A section of the **Forge Suite** repository since 2026-10-06 (D-60) — read the suite's `CLAUDE.md` too. Tags: `forgekit-vX.Y.Z`; issues in `jetomev/forge-suite`.*

*How this project is built, tested and shipped. Written for the AI co-developer, and public on purpose: it is part of how the human + AI method is documented.*

## What it is
A small Python library on top of [Textual](https://textual.textualize.io): the shared window shell of the Forge Suite (title bar, menu bar, full-width workspace, floating dialogs, Catppuccin colours). Apps subclass `ForgeApp`. **Adopters:** bitlaForge, alacrittyForge, grubForge, nogForge, hypeForge (Help & Keys), displayForge; **next:** welcomeForge, fileForge. A change here lands in every app, so it is made carefully and tested in more than one of them.

## Non-negotiables
- **Readable and usable on a plain text console (`TERM=linux`)**, not only in a terminal window (issue #1, the promise written down 2026-10-01). It does not have to look the same there; it must stay readable and usable. Every new piece of styling goes through the semantic colour roles and the glyph table, never a literal colour or a fancy character on its own.
- **The window paradigm is locked** (README, "Keyboard model"): title bar, menu bar with underlined letters (`Ctrl+<letter>`), Help then Quit last, full-width workspace, floating dialogs with a fixed footer, no green buttons. Changing it is Javier's call.
- **A library proves its API through apps.** No 1.0 until grubForge, alacrittyForge, bitlaForge and nogForge all run on it.
- **Credit, never comparison.** Catppuccin is credited; we never frame forgekit against other toolkits.

## How to run and test
- The demo: `PYTHONPATH=. python examples/demo.py` (forgekit is not pip-installed on the desktop).
- Tests: `python -m unittest discover -s tests -v` (Python's built-in runner, nothing to install; headless through Textual's Pilot). **Report the test count at every release**; a drop means something was deleted silently.
- **Check layout by position, not by existence**: a test that finds a widget proves nothing about where it is drawn (lesson from v0.1.0, where logic tests passed while the bar was visibly broken).
- **Console preview:** `python tools/console-preview.py <command>` runs any Forge app as if on `tty3` (`TERM=linux`, 16 colours, the console font's character set) and saves a PNG; characters the font cannot draw are marked in red. Needs `python-pyte` (installed through nog). Every release's test matrix includes a console run, and **Javier's run on a real `tty3`** is the final check.
- **Real console, on a VM** (how v0.4.0 was proven, 2026-10-01): snapshot the KognogOS VM, copy the tree in through the qemu guest agent, start the app on **tty8** with `openvt -c 8 -s -f -- runuser -u <user> -- env -i TERM=linux … <app>`, press keys with `virsh send-key`, copy `/dev/vcsa8` out (`base64` through the agent) and redraw it with `python tools/vcsa-shot.py`. Then revert the VM to its snapshot. **Use tty7 or higher:** logind starts a login program (`autovt`, `NAutoVTs=6`) on tty1–6 when one becomes active, and it hangs up anything else on that console. On tty3/tty6 that produced a half-erased menu and keys that never arrived, which looked like an app bug (2026-10-01). (`virsh screenshot` does not work on these VMs' 3D displays.)
- The real console differs from a terminal in ways the emulation must copy: **underline shows as cyan and italic as green**, bold shows as bright, and only the 8 basic colours are reliable as backgrounds. `console-preview.py` models these and flags any letter drawn in its own background colour.
- Screenshots for the README: `python docs/screenshots/generate.py`.

## Documentation, at every step
- `TODO.md` is updated after every step; it is the handoff between sessions.
- The README stays accurate top to bottom at every commit. Roadmap and changelog are newest first; the README keeps only upcoming work and the two most recent releases, older ones live in `docs/CHANGELOG.md` / `docs/ROADMAP.md`.
- Findings are numbered F-n and each gets an issue, opened with a full explanation and closed with one.
- After every push: a Vault entry in `~/Google Drive/Rullynastre/ForgeKit/`.
- Plain words throughout. The readers are not engineers.

## Release discipline
- Version in **every** surface at once: `pyproject.toml`, `forgekit/__init__.py`, README, the AUR `python-forgekit` PKGBUILD (in lockstep on content, not only `pkgver`).
- Commits: `<scope>: …` for work, `release: vX.Y.Z — <tagline>` for the release commit; every commit GPG-signed and carrying the co-author trailer.
- Tags are annotated and signed: `git tag -s vX.Y.Z -m "…"` (a bare `git tag` fails here because tag signing is on).
- Order: push `main` + tag → GitHub Release with notes and signed artifacts → AUR → check with a fresh install. Then the adopting apps move to the new version, one at a time.
- Test matrices go in `testing/`, named `YYYYMMDD - Test Matrix for forgekit vX-Y-Z.md` (hyphens in the version).
