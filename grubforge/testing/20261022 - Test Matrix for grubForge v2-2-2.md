# grubForge v2.2.2 — Test Matrix

*Written 2026-10-22. What changed: the launcher entry ships with the package ([#37](https://github.com/jetomev/grubforge/issues/37)). Everything else is 2.2.1's, which passed on 2026-10-08 and 2026-10-11 (see the Test Results files here).*

## 1 · Built and checked by Claude (2026-10-22)

| ID | What | Proven by | Result |
|---|---|---|---|
| 1.1 | The entry `grubforge.desktop` is in the source, valid, `Terminal=true`, one main category | `tests/test_desktop_entry.py` (seen failing without the file); `desktop-file-validate` finds nothing | **PASS** |
| 1.2 | The version is 2.2.2 in the code, the man page, the README, the changelog and the roadmap | read by hand; the man page fixed (it said 2.2.0 in 2.2.1) | **PASS** |
| 1.3 | All tests | `python -W always -m unittest discover -s tests`: **87 + 25 script checks (86 at 2.2.1)**, all passing | **PASS** |
| 1.4 | The release files rebuild byte for byte from the signed tag | rebuilt with the same `git archive --mtime` and compared | **PASS** |
| 1.5 | The AUR recipe builds the package from the published release: checksum and signature pass, the tests inside the build pass, the entry is in the package (`usr/share/applications/grubforge.desktop`) | `makepkg -f` in `~/Programs/aur-grubforge` | **PASS** |

## 2 · Javier's run (at the keyboard)

Setup: `forge-suite/scripts/install-local-builds-20261022.sh` installs the three locally built packages through nog (it asks for the password) and checks their entries; it logs to `forge-suite/logs/`.

| ID | Task | EXPECT | Result | Notes |
|---|---|---|---|---|
| 2.1 | Run the install script (above) | it ends with **OK**, and lists **grubforge 2.2.2-1** | | |
| 2.2 | `grubforge --version` | **grubForge 2.2.2** | | |
| 2.3 | `ls /usr/share/applications/grubforge.desktop` | the file is there (the package's own entry) | | |
| 2.4 | `man grubforge`, look at the top line | **grubForge v2.2.2** (2.2.1's man page still said 2.2.0) | | |
| 2.6 | Open the launcher (**Win + Space**), type `grubf` | **one** grubForge entry (hypeForge's own copy hides the package's: same name, no duplicate); Enter opens it in its floating window, on the Overview | | |
| 2.7 | A quick look: Settings ▸ Timeout, then **Q** | it works as in 2.2.1; it closes with its closing note | | |
| 2.8 | hypeForge Settings ▸ **Boot Menu** | grubForge opens there as before (no Quit in its bar) | | |

**Done when** every row of §2 passes. Then: the AUR push (one push, this version), and #37 closes.
