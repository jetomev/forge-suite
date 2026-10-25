# Test Matrix — nightForge v1.1.1 (the tray icon steps aside on every hypeForge bar)

*2026-10-25 · the KognogOS test desktop (Sway, hypeForge, KDE style · Dark Blue). With hypeForge's D-117: the night light lives in Quick Settings; the moon leaves every bar. Results go in a Test Results file next to this one.*

| # | What | How | Who | Result |
|---|---|---|---|---|
| C1 | Automatic tests | `python3 -m unittest discover -s tests -t .`: 27, 0 warnings | Claude | ✅ 2026-10-25 |
| C2 | The package builds from the published release | `makepkg -f`: sources checked (sha256 + signature), 27 tests in `check()` | Claude | ✅ |
| C3 | A clean Arch build | the test VM, `makechrootpkg` | Claude | ✅ 2026-10-25 |
| 1 | Install the local package | `nog install ~/Programs/aur-nightforge/nightforge-1.1.1-1-any.pkg.tar.zst` | Javier | ✅ 2026-10-25 |
| 2 | The tray icon is gone | after Claude restarts nightForge's tray: no ☀ / ☾ / ○ night-light icon in the tray | Javier | ✅ 2026-10-25 |
| 3 | The night light from Quick Settings | Quick Settings → the Night light tile → its page: the switch, the sentence, the warmth, Warm now, Automatic; ‹ back | Javier | ✅ 2026-10-25 |
| 4 | nightForge from the page | the icon at the page's bottom right opens nightForge (1.1.1 in its title) | Javier | ✅ 2026-10-25 |
| 5 | Next login: no moon on the bar | log out and in: the bar has no moon; still no tray icon; the night light works as before | Javier | ✅ 2026-10-25 |
