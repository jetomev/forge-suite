# nightForge — changelog

*Newest first.*

### 1.0.0 — October 9, 2026 · warmer screens in the evening, your way ([#44](https://github.com/jetomev/forge-suite/issues/44))

From Javier's issue (#44, October 7) to release in one afternoon: designed (two drafts, D-2), approved (D-3), with a tray icon of its own (D-4).

- **Night Light:** what is happening now; on or off (at once, and at every login); **Right now** — Automatic, Warm Now, Daylight Now, holding until Automatic or logout; the evening warmth in five steps with words (3000 very warm … 5000 just a touch) or any number; a 10-second **Preview** that goes back by itself.
- **Schedule:** by the sun at your place (two numbers; the sun times worked out on the computer with NOAA's formulas, nothing looked up online) or fixed times with a fade.
- **Saving:** a review in a pop-up, like Preview (D-2); a backup (the last 20 kept); the night light restarts with the new settings at once, and at every login.
- **The tray icon** (D-4): a muted ☀ by day, a mustard ☾ while warm, a dim ○ when off — Javier's colours (D-5); a click shows its menu (D-6): Automatic · Warm Now · Daylight Now · Turn Off / Turn On · Open nightForge. Any bar with a tray.
- **At login** hypeForge runs `nightforge start`: wlsunset as the settings say, and the tray icon. `nightforge status` says what it's doing.
- **Inside hypeForge Settings** as the Night light page; a three-page manual.
- **Found and fixed before release:** spaces lost after bold words, a word said twice, narrow time fields (the pictures); a status that said "off" while hypeForge's old night light ran; Schedule's place boxes spilling onto their note (Javier's run).
- **Proven at sunset** on the test desktop: the screens warmed by themselves and the tray icon turned mustard (Javier, 10 Oct).
- Tests: **23** (core 12, the tray on a private bus 4, pages 7); 10 behaviours broken on purpose, 10 caught. Warnings: 0. `scripts/bench-start.py`: the real wlsunset on a hidden Sway, 14 of 14, the desktop's night light untouched.
