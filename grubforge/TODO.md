# grubForge — the list

**Current release: v2.2.0** (8 Oct 2026, GitHub + AUR); before it v2.1.0 (4 Oct). **v2.2.0 released 2026-10-08 (GitHub + AUR; Javier on the installed package: "all perfect!")

**Updated after every step.** The full story behind each item is in its GitHub issue.


## 2026-10-22 · Moved into the Forge Suite (the last app)
- [x] **Moved into `forge-suite/grubforge`** (Javier: "can you?" — go): `git subtree add` with the full history (signed merge `81ac492`), all 22 tags re-created signed as `grubforge-v0.1.0…v2.2.2`, open issues moved (#34 → forge-suite#119, #35 → #120), no open pull requests and no forks, the old repository got a moved note (and a thank-you for its 10 stars, which stay there) and is archived, `~/Programs/grubforge` → a shortcut (the old folder in `~/Programs/_moved-into-forge-suite/`)
- [x] The app's own links (`--help`'s manual, About's Code) point at the suite (`tests/test_home.py`, seen failing first)
- [ ] **At the next version:** the release from forge-suite (`scripts/release-app.sh grubforge X.Y.Z`), the AUR recipe repointed at `jetomev/forge-suite` releases

## 2026-10-22 · The project's board
- [x] **A board for this project** (https://claude.ai/artifact/2idA8cXm3crj2kqhMtQmVE): this TODO as a page beside the chat — calling the project opens it first (mindForge boards, `.board`). Ticks made on the page come back here

## 2026-10-12 · CLAUDE.md keeps only this project's own rules
- [x] **One rule, one level** (Javier, 2026-10-12): the 'never the persona names here' line removed; the names come from the global agreement. Commit pushed the same night.

## 2026-10-11 · What it needs, measured
- [x] **What it needs, measured** (2026-10-11, forge-suite#91): `docs/PACKAGING.md` + `tests/test_needs.py`. The AUR 2.2.0 build **failed in a clean system** — F-8 #41: reload() read the system's own /etc/default/grub (fixed `2f52058`); the recipe now depends on grub (+ os-prober optional)
- [x] **2.2.1** — GitHub Release v2.2.1 (signed, 2026-10-11), 86 tests at the tag; AUR `2635ffd` after Javier's local test ✅

## At the next release
- [x] **2.2.2 released 2026-10-22** — GitHub `v2.2.2` (reproducible), Javier's local test all pass, AUR `6abd560` pushed, #37 closed
- [x] **The launcher entry (#37)** — in 2.2.2 (2026-10-22, Javier: ship it now); — `grubforge.desktop` + `tests/test_desktop_entry.py` are in the repo (2026-10-22, the KognogOS clean-house); at the next version the AUR recipe adds `install -Dm644 grubforge.desktop "${pkgdir}/usr/share/applications/grubforge.desktop"`, `checkdepends=('desktop-file-utils')` and `desktop-file-validate grubforge.desktop` in `check()`; then close #37, and hypeForge's own copy can go
- [ ] **The AUR description, at the next release** (Javier, 2026-10-09): the AUR `pkgdesc` (and `.SRCINFO`) gets the same "where it runs" words as the README, GitHub About and kognogos.org — distribution · desktop · plain text console. Not pushed on its own: AUR pushes stay one per proven version.

## v2.2.0 — keys from forgekit 0.10.0, Boot Menu, --hypeforge, button labels · released 2026-10-08 (GitHub + AUR; Javier on the installed package: "all perfect!")
Javier's findings running grubForge inside hypeForge Settings (8 Oct 2026):
- [x] **#38 F-6**: Help had no number; "1-5 screens" confusing → numbers 1-6 (Help is 6) and Ctrl + the underlined letter come from forgekit 0.10.0; the bar says "1-6 menu"; Keys list, manual, man page, README
- [x] **#39 F-7**: "Boot menu" → "Boot Menu" (tab, screen heading, manual, man page, README)
- [x] **#40**: `--hypeforge` (any case): no Quit, Q / Ctrl+Q do nothing, Settings closes it through grubForge's own question; not in `--help`/man page; README "Inside hypeForge Settings", manual page 1, CLAUDE.md, changelog
- [x] **#40 / 3 Oct 2026 — button labels in Javier's format:** "Words In Title Case (k)", the key in brackets after the words (every Button, review, quit and changes-bar label)
- [x] **Round 2 (Javier's second run, 8 Oct):** forgekit's letter rule (first letter, else the next free one; Help H, Quit Q; Ctrl+R kept) → **Settings Ctrl+S, Backups Ctrl+A**, grubForge's `"acc"` removed; 6 again closes Help, the open menu lit; About and License as pages, Esc back. Keys list, manual, README, man page, changelog, matrix
- [x] **Round 3 (Javier: "yes, Keys and Manual as pages too"):** the manual through forgekit's `show_manual` (F1 still opens the right page; Esc back to the screen, Backspace to the previous manual page); Keys a page through forgekit
- [x] Tests 78 → 108 (`tests/test_v220.py`, 30 new, each seen failing with its fix out); warnings 3 → 3
- [x] Test matrix: `testing/20261008 - Test Matrix for grubForge v2-2-0.md`
- [x] **Javier runs the matrix** (§2–§6), on the desktop and inside hypeForge Settings — **done**: run 2026-10-08 inside hypeForge Settings, passed (`testing/20261008 - Test Results for grubForge v2-2-0.md`); 2.2.2's matrix carries the next run (ticked 2026-10-22: the results file shows it)
- [x] At release (done 2026-10-08) (lead): forgekit 0.10.0 released + on the AUR first; AUR recipe `python-forgekit>=0.10.0` and **`tests.test_v220` added to `check()`**; tag, GitHub release, issues #38 #39 #40 closed, AUR push after Javier's local test, badge cache-buster after; Vault
- [ ] Screenshots in `screenshots/` still show "Boot menu" and the old button labels (`scripts/make-screenshots.py`)
- [x] **Fixed in forgekit 0.10.0 (2026-10-08, found by this build):** a window open over the app keeps its keys, so Ctrl+E and Ctrl+K in the Rename field edit the text again and nothing switches the screen behind it (forgekit test `test_a_dialog_keeps_its_keys`; grubForge's 75 tests pass on it)

## Done · v2.1.0 — polkit's password in grubForge's own box, text console included · released 2026-10-04 (GitHub + AUR eedcc7b, #36 closed)
- [x] forgekit's InAppPolkitAgent at start; manual (On a text console, Won't start) updated; 53 tests
- [x] KognogOS VM tty3: wrong password → try again; right one → backup as root (source and installed 2.1.0rc1)
- [x] Javier's desktop test passed ("perfect!") → released after forgekit 0.6.0 (AUR recipe: python-gobject + forgekit>=0.6.0, local only)
- [x] Decide (Javier): over ssh the policy refuses (allow_any=no) — keep? — **keep** (Javier, 2026-10-22, the KognogOS stage 00 answers) (ticked 2026-10-22 by the KognogOS link check)

## Next
- [x] Javier: `nog install grubforge` on the desktop: 2.0.0-1 + python-forgekit 0.5.0-1, verified 2 Oct (public AUR path works)
- [ ] A look at the real desktop menu with 2.0 (its old #20 copy should show "Drop the old copy")
- [ ] #34 write `/etc/default/grub.d` on Debian/Ubuntu — **needs Javier's design call**: edit the file that sets it, or add a grubForge file late in the order
- [ ] #35 rename/reorder Fedora entry files
- [ ] Keep the test VMs (gf-debian, gf-ubuntu, gf-fedora, gf-opensuse; snapshot `fresh`) for the next release

## Done — v2.0.0 (released 2 Oct 2026)
Javier's brief (2 Oct): *"screens done with high quality UI and easy to use structure … caring for formatting, use of colors, contrasts, and following flow of use from selecting, tabbing, buttons … leave as little to the user to write where options are known to select from … besides the help shortcuts, a manual on how to use it."*

- [x] Research (2 Oct): inventory of every screen/setting today; forgekit's API and gaps; how well-regarded TUIs do settings, pickers, apply/preview, manuals
- [x] Design approved (2 Oct): https://claude.ai/artifact/EM3avQE6fn4EXYHnz9674R · copy in `docs/design/v2.0.0-screens.html`. Javier's rulings:
  1. Settings as a **form** with visible controls
  2. **Save** and **Rebuild** are two buttons; saved stays saved; the bar shows "saved, not rebuilt"
  3. **Plain names**, GRUB name in the help line
  4. Entries from other tools (snapshots) **stay fixed** (#20)
  5. **All major distributions** (#24): Arch, Debian/Ubuntu, Fedora/RHEL (BLS entries!), openSUSE, Gentoo/Void; non-GRUB systems open read-only
  6. **Closing note** in the terminal; **quit warns** when something is saved but not rebuilt (or not saved)
  *"So far, it is looking very good! This pages where you do work and show me are very good to visualize before we go bananas."*
- [ ] Design still to show: the Boot menu on Fedora-style (BLS) systems
- [x] Phase 1 · forgekit v0.5.0 (2 Oct, forgekit `c13c238`, not released — proven here first): hint bar, changes bar + review window, filter list, notices, progress window, manual viewer, roles (changed, info), glyphs, styles for lists/switches/checklists/radio
- [x] Phase 2 · frame + Overview + Settings (form), Save, Rebuild, quit warning, closing note — `f52ca05` + fixes; **real save proven in the KognogOS VM** (timeout 5→3: backup, write, rebuild, `set timeout=3`; Save-only → "saved, not rebuilt" → quit asks → F9 clears). Also #22 (--version/--help) and #24 groundwork (grubenv + helper picks the tool)
- [x] Phase 3 · Boot menu (+ Add an entry, Find other systems, #20 fixed entries + the old copy dropped) — real save and restore proven in the VM; found + fixed the `20_memtest86+` marker bug. Open O-1: the UEFI entry's `if` guard isn't copied into a saved order
- [x] Phase 4 · Themes (preview, use, install through the checked helper verb `theme-install`) + Backups (plain reasons, what a restore changes, boot-order copy kept beside each backup) — proven in the VM incl. a refused attack archive
- [x] Phase 5a · manual (14 pages, F1 → the right page), console (every screen passes at 100×30 and 128×48), `--version`/`--help` (#22), distro detection (#24) — VMs for other distributions still to do (5b)
- [x] Phase 5b · VMs per family (`scripts/make-test-vms.sh`, snapshot `fresh` each): **Debian 13, Ubuntu 24.04, Fedora 44, openSUSE Tumbleweed all PASS** — a real save reached grub.cfg in each; found + fixed F-1 (unset list staged a change), F-2 (/etc/default/grub.d overrides silently won), F-3 (Fedora Boot menu), F-4 (empty vs unset, openSUSE)
- [x] Phase 6 · release: Javier's run PASS (§10); forgekit 0.5.0 released + AUR first; grubForge 2.0.0 docs, tag, GitHub release, AUR; issues #17 #19 #20 #21 #22 #24 #25 closed, findings F-1…F-5 as #29–#33 (opened + closed); memory + Vault
- [ ] In-app manual (besides the help shortcuts)
- [ ] Console mode readable (#21)
- [ ] Test matrix `testing/20261002 - Test Matrix for grubForge v2-0-0.md` — filled phase by phase; §9 needs VMs for Debian/Ubuntu/Fedora/openSUSE; §10 Javier's run

## Open issues to fold in or decide
- [x] #22 `grubforge --version` launches the TUI — **done**: fixed in v2.0.0, #22 closed (ticked 2026-10-22 by the KognogOS link check)
- [x] #19 frozen boot entries make /etc/default/grub edits inert, with no warning — **done**: fixed in v2.0.0, #19 closed (ticked 2026-10-22 by the KognogOS link check)
- [ ] #20 saving a custom order duplicates entries from other generators (41_snapshots-btrfs)
- [ ] #24 Fedora/openSUSE/RHEL use /boot/grub2 and grub2-mkconfig
- [ ] #25 test matrix 11.A/11.B can't run on UEFI Arch
- [ ] #17 regeneration / stale-state edge cases

## Done
- v1.1.3 (29 Sep) — #28 entry sources read from grub.cfg markers; tests/ (25 checks)
- v1.1.2 (29 Sep) — #27 the distro name read from os-release
- Earlier: docs/CHANGELOG.md
