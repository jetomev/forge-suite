# Test Results — nightForge v1.1.1 (the tray icon steps aside on every hypeForge bar)

*2026-10-25 · Javier's run of [the matrix](20261025%20-%20Test%20Matrix%20for%20nightForge%20v1-1-1.md) on the KognogOS test desktop (Sway, hypeForge, KDE style).*

**Result: PASS — every row. No findings.** On the AUR as 1.1.1-1 (`65394dc`).

| # | What | Result |
|---|---|---|
| C1 | Automatic tests: 27, 0 warnings | ✅ |
| C2 | The package builds from the published release (sources checked, 27 tests in `check()`) | ✅ |
| C3 | A clean Arch build in the test VM | ✅ |
| 1 | The local package installed (`nog install`) | ✅ Javier |
| 2 | The tray icon is gone (the old tray process stopped by its number, the 1.1.1 one started: "Passive") | ✅ Javier |
| 3 | The night light from Quick Settings (its tile → its page) | ✅ Javier |
| 4 | nightForge from the page's bottom-right icon | ✅ Javier |
| 5 | Next login: no moon on the bar, still no tray icon, the night light as before | ✅ Javier, 18:52 (*"Night Light did not appeared, and everything is working well"*) |

**Seen at that login, not nightForge's:** the bar crashed 2 s after starting (its volume piece reached the sound system before it was ready) and hypeForge's bar guard brought it back within seconds — hypeForge's, recorded there.
