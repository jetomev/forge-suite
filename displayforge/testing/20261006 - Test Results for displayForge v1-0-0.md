# Test Results — displayForge v1.0.0

*2026-10-06 · against the [Test Matrix](20261006%20-%20Test%20Matrix%20for%20displayForge%20v1-0-0.md). Javier's words where he gave them.*

| # | Result |
|---|---|
| 1–6 | ✅ Javier: *"Everything was working well with displayForge"*; *"looks and works wonders"* |
| 7 | ❌ → ✅ **F-2**: the screens stayed dark after Identify. Fixed (see below); Javier's re-run pending |
| 8 | ✅ (it is where Javier brought his screens back during F-2) |
| 9 | ❌ → ✅ **F-1**: the first letter typed closed the app. Fixed |
| 10 | 🔄 Javier: *"I still have to test a little more the arrange section, but so far good"* |
| 11 | ❌ → ✅ **F-3**: there was no manual in Help. Seven pages added |
| 12 | ✅ **50 tests, 0 warnings** |
| 13–15 | ⬜ **Not run yet** — said so in the release notes; findings become 1.0.x fixes |

## Findings

### F-1 · Typing a screen name closed the app
The handler's helper was named `_name`, which Textual already uses on every widget; the first keystroke called it and the app crashed. Renamed; a typing test, and a permanent check that no name of ours reuses one of Textual's (it sees `_name`, so it would have caught this). Commit `22a7a08`.

### F-2 · Screens stayed dark after Identify
During each three-second dim, the previous round's answer buttons were still up; a click there cancelled the running step before its restore. Now no buttons while a screen is dark, and each dim + restore runs in its own process (like the screen-change safety timer), read back and retried until the screen reports it. Tested in the failing direction: the step cancelled mid-dim, a screen that ignores two restores, one that never comes back. Commit `328db58`.

### F-3 · No manual in Help
Seven plain-word pages; Help → Manual and the M key. Commit `5d4a2e2`.
