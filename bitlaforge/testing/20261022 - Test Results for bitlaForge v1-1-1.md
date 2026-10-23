# Test Results — bitlaForge v1.1.1

*2026-10-22 · the KognogOS test desktop (Sway, three screens). Matrix: [20261022 - Test Matrix for bitlaForge v1-1-1](20261022%20-%20Test%20Matrix%20for%20bitlaForge%20v1-1-1.md). Issue: forge-suite#118.*

## 1 · Automated (Claude)

- `python -W always -m unittest discover -s tests`: **90**, all passing. ✅
- The release files rebuild byte for byte from the signed tag. ✅
- The AUR recipe built the package from the published release: checksum and signature pass, the tests inside the build pass, `usr/share/applications/bitlaforge.desktop` is in the package. ✅
- AUR pre-flight before the push: the sha256 against the downloaded tarball, `gpg --verify` of the `.asc`, `makepkg --printsrcinfo` against `.SRCINFO`, the commit carrying only `PKGBUILD` + `.SRCINFO`. ✅

## 2 · Javier's run

Installed through nog from the locally built package (`forge-suite/scripts/install-local-builds-20261022.sh`, 22:58): `bitlaforge 1.1.1-1`, the entry installed and valid.

| ID | Task | Result | Notes |
|---|---|---|---|
| 2.1 | Install through the script | **PASS** | nog handed off to pacman; the script ended with OK |
| 2.2 | `bitlaforge --version` | **PASS** | bitlaForge 1.1.1 (checked by Claude on the installed package) |
| 2.3 | `/usr/share/applications/bitlaforge.desktop` | **PASS** | there, valid (checked by Claude) |
| 2.4–2.5 | Where it points | **PASS** | `--help`'s manual and About's Code: `github.com/jetomev/forge-suite/tree/main/bitlaforge` (checked by Claude in the installed code) |
| 2.6 | The launcher: one entry, opens in its floating window | **PASS** | Javier, 2026-10-22 |
| 2.7 | A quick look, then Q | **PASS** | Javier |
| 2.8 | Inside hypeForge Settings (Mining) | **PASS** | Javier |

**Verdict:** every row passes (Javier: *"all three pass"*). The AUR push follows: one push, this version; then forge-suite#118 closes.
