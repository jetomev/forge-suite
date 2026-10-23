# Releasing one Forge Suite app

*Every app in this repository keeps its own version, its own tag `<app>-vX.Y.Z` and its own AUR package (D-60). This is how one of them ships, written down 2026-10-22 from the releases that proved it (displayForge, sudoForge, workspaceForge, nightForge, forgekit) — plus one fix found while writing it: release files are now reproducible.*

The order never changes: **the maintainer's run passes → docs and version → signed tag → GitHub Release → AUR recipe → the maintainer installs the local package and tests it → only then the AUR push.** GitHub goes first because the AUR recipe downloads the release's files.

## 1 · Before anything ships

- The app's tests pass: `python -m unittest discover -s <app>/tests`. **Report the count**; a drop means something was deleted silently. Count warnings and report the change.
- The test matrix is in `<app>/testing/YYYYMMDD - Test Matrix for <App> vX-Y-Z.md` (hyphens in the version), and the maintainer's run of it has passed. Findings are F-n, each with an issue opened and closed.
- `<app>/docs/PACKAGING.md` lists everything the app imports or runs (`tests/test_needs.py` fails on an unlisted one). The AUR `depends` are copied from it, never typed from memory.

## 2 · The version, everywhere, in one commit

`docs(<app>): README + version bump for vX.Y.Z` — the version in **every** surface of the app (its code, README, CHANGELOG and ROADMAP newest first, manual, CLAUDE.md, the help pages). The README keeps only upcoming work and the two most recent releases.

## 3 · The signed tag

```
git tag -s <app>-vX.Y.Z -m "<App> X.Y.Z — <tagline>"
git push origin main <app>-vX.Y.Z
```

## 4 · The release files

```
scripts/release-app.sh <app> X.Y.Z
```

It checks the tag's signature, then builds `dist/<app>-X.Y.Z/`:

- `<app>-X.Y.Z.tar.gz` — `git archive` of **only the app's folder** at its tag, under the prefix `<app>-X.Y.Z/`, gzip `-n -9`, **every file dated the tag's commit time** (`--mtime`).
- `<app>-X.Y.Z.SHA256SUMS`, and a `.asc` signature for each of the two (the maintainer's key `32E1D2AB9380BFD6BFE3BC1EAC2A3407CC070F9E`).

`--no-sign` makes the same files unsigned (a dry run, no password box). The script logs to `logs/` and **never publishes**: it prints the GitHub command.

*Why the pinned time:* without it each build is stamped with the moment it ran, so nobody could rebuild a published file to check it. Releases up to 2026-10-22 are like that (nightForge 1.1.0 and displayForge 1.1.1 rebuild to the same files and contents, other file times); from now on they rebuild byte for byte.

## 5 · The GitHub Release

```
gh release create <app>-vX.Y.Z -R jetomev/forge-suite --title "<App> X.Y.Z — <tagline>" --notes-file <notes> \
  dist/<app>-X.Y.Z/<app>-X.Y.Z.tar.gz dist/<app>-X.Y.Z/<app>-X.Y.Z.tar.gz.asc \
  dist/<app>-X.Y.Z/<app>-X.Y.Z.SHA256SUMS dist/<app>-X.Y.Z/<app>-X.Y.Z.SHA256SUMS.asc
```

- **Rich notes:** what changed in plain words, the findings fixed (with their issues), the test count, how to install.
- **Latest** (decided 2026-10-22; the maintainer left it to Claude): one repository holds many apps, so only one release can be Latest — **the newest app release takes it**, so people landing on the repository see an app they can install; **forgekit, the shared library, never does** (`--latest=false`).
- Then check it: `scripts/release-app.sh <app> X.Y.Z --verify` downloads the published files, checks both signatures and the checksum, rebuilds from the tag and compares byte for byte.

## 6 · The AUR recipe

In `~/Programs/aur-<pkg>/` (packaging only: `PKGBUILD`, `.SRCINFO`, `.gitignore` — never build output):

- `pkgver=X.Y.Z`, `pkgrel=1`; the source is the release's tarball **and** its `.asc`, with `validpgpkeys=('32E1D2AB9380BFD6BFE3BC1EAC2A3407CC070F9E')`; `sha256sums` from the release's SHA256SUMS; `depends` from `docs/PACKAGING.md`; `check()` runs the app's tests.
- Pre-flight, all read-only: the sha256 against the downloaded tarball · `gpg --verify` the `.asc` · `makepkg --printsrcinfo | diff - .SRCINFO`.
- `makepkg -f` (it downloads the published files and runs `check()`), and a build in a clean Arch (the KognogOS VM) before trusting it.
- **Dependency order:** a library (`python-forgekit`) is on the AUR before the apps that need it.

## 7 · The maintainer's test, then the AUR push

The maintainer installs the locally built package — `nog install ./<pkg>-X.Y.Z-1-any.pkg.tar.zst` — and tests it. **Only on a pass:** push to the AUR, one push per proven version (a fix found during the test goes into the same unpublished version). The AUR checks every commit in a push: an unpushed range with stray files is rebuilt as one clean commit (`git reset --soft origin/master`, add the three files, commit). Then a fresh install through the AUR helper proves it.

## 8 · Every surface, the same day

Issues closed with a full explanation · the README's row · kognogos.org's card (only for an app approved to be public) · the Vault entry · the project's memory and next-session plan · the KognogOS board (its link check shows whatever moved: `kognog/scripts/board-links.py check`).
