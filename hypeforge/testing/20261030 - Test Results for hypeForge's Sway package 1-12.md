# Test Results — hypeForge's Sway package 1.12 (2026-10-30)

*The KognogOS package `sway-hypeforge` (D-111) after Javier's choices D-127 (KognogOS's own package source only)
and D-128 (the system's Sway held at the version it is built from), and the login starter's change to run the
package's copy first. Run by Claude in the `kognog-hypeforge` VM (snapshot before: `sway-opt-before`, after:
`sway-opt-tested`). Javier's own desktop was not touched: the package is not installed there.*

## What changed

- `hypeforge-session` runs `/opt/sway-hypeforge/bin/sway` when it is there, else the home-folder build (`build.py`), with
  the same version check and fallback as before.
- `PKGBUILD`: `depends=("sway=1:${pkgver}" …)` in place of `>=` (D-128).
- `login-test.sh`: with the package installed, a case for "home build gone".

## Results

| # | Case | Expected | Result |
|---|---|---|---|
| 1 | No package (as on Javier's desktop today): versions match | the home-folder build, no fallback flag | ✅ `~/.local/opt/sway-hypeforge/current/bin/sway` |
| 2 | No package: Sway updated to 1.13 (faked) | the system's Sway, flagged `1.12:1.13` | ✅ |
| 3 | No package: our build broken | the system's Sway, flagged `none:1.12` | ✅ |
| 4 | Package built in the VM (`makepkg -s`, Sway's signature checked, 5 patches) | builds | ✅ `sway-hypeforge-1.12-1` (5.4 MB). One stray `libfakeroot internal error: payload not recognized` line; exit 0 |
| 5 | Installed with `nog install --yes ./…pkg.tar.zst` | installs; depends on `sway=1:1.12` | ✅ (without `--yes` and no keyboard, nog stops and says to add it) |
| 6 | Package installed: versions match | `/opt/sway-hypeforge/bin/sway`, no flag | ✅ |
| 7 | Package installed: Sway updated (faked) | the system's Sway, flagged | ✅ |
| 8 | Package installed: home build gone | still `/opt/…` | ✅ |
| 9 | Package's copy broken (`chmod -x`, by hand) | the home-folder build | ✅ |
| 10 | The hold: a fake `sway 1:1.13` package, through pacman and through nog | refused; nothing changed | ✅ `breaks dependency 'sway=1:1.12' required by sway-hypeforge`; still `sway 1:1.12-4` |

## Findings

- **nog's wording on the hold (for nog):** nog shows pacman's line, then says *"you answered no, or it hit a problem
  shown above"* and suggests `nog update`. For a held Sway that misleads: it should say Sway is held by
  `sway-hypeforge` until our rebuild is out. To be filed in nog.
- The VM's old `~/.config/sway/config` (written by the 10-17 run, before the script marked its own) made the guard
  refuse to run, as designed; moved aside to `config.before-20261030`.

Not tested here: a real login on a screen through the package (the hidden-screen runs start Sway the same way the
login does), and installing the package on Javier's desktop (his step, later).
