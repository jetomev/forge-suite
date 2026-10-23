# alacrittyForge v1.1.1 — Test Matrix

*Written 2026-10-22. What changed: the launcher entry ships with the package ([forge-suite#114](https://github.com/jetomev/forge-suite/issues/114)), and alacrittyForge moved into the Forge Suite (its links point at the new home). Everything else is 1.1.0's, which passed on 2026-10-08 (see the Test Results files here).*

## 1 · Built and checked by Claude (2026-10-22)

| ID | What | Proven by | Result |
|---|---|---|---|
| 1.1 | The entry `alacrittyforge.desktop` is in the source, valid, `Terminal=true`, one main category | `tests/test_desktop_entry.py` (seen failing without the file); `desktop-file-validate` finds nothing | **PASS** |
| 1.2 | No link in the app points at the archived repository; `--help` names the manual in the suite | `tests/test_v111.py` (seen failing on 1.1.0's links) | **PASS** |
| 1.3 | All tests | `python -W always -m unittest discover -s tests`: **113 (109 at 1.1.0)**, all passing | **PASS** |
| 1.4 | The release files rebuild byte for byte from the signed tag | `scripts/release-app.sh alacrittyforge 1.1.1 --verify` | **PASS** |
| 1.5 | The AUR recipe builds the package from the published release: checksum and signature pass, the tests inside the build pass, the entry is in the package (`usr/share/applications/alacrittyforge.desktop`) | `makepkg -f` in `~/Programs/aur-alacrittyforge` | **PASS** |

## 2 · Javier's run (at the keyboard)

Setup: `forge-suite/scripts/install-local-builds-20261022.sh` installs the three locally built packages through nog (it asks for the password) and checks their entries; it logs to `forge-suite/logs/`.

| ID | Task | EXPECT | Result | Notes |
|---|---|---|---|---|
| 2.1 | Run the install script (above) | it ends with **OK**, and lists **alacrittyforge 1.1.1-1** | | |
| 2.2 | `alacrittyforge --version` | **alacrittyForge 1.1.1** | | |
| 2.3 | `ls /usr/share/applications/alacrittyforge.desktop` | the file is there (the package's own entry) | | |
| 2.4 | `alacrittyforge --help`, look at the last line | **Manual:** points at `github.com/jetomev/forge-suite/tree/main/alacrittyforge/…` (the new home) | | |
| 2.5 | In the app: Help ▸ **About**, look at **Code** | it points at `github.com/jetomev/forge-suite/tree/main/alacrittyforge` | | |
| 2.6 | Open the launcher (**Win + Space**), type `alacr` | **one** alacrittyForge entry (hypeForge's own copy hides the package's: same name, no duplicate); Enter opens it in its floating window, on Alacritty's settings | | |
| 2.7 | A quick look: Settings ▸ Text ▸ Size, then **Q** | it works as in 1.1.0; it closes with its closing note | | |
| 2.8 | hypeForge Settings ▸ **Terminal** | alacrittyForge opens there as before (no Quit in its bar) | | |

**Done when** every row of §2 passes. Then: the AUR push (one push, this version), and forge-suite#114 closes.
