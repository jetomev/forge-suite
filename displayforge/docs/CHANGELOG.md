# displayForge — changelog

*Newest first.*

## 1.0.0 — 2026-10-06 · the first release

**Everything the approved design asked for** ([D-2](DECISIONS.md)), declared done by Javier ([D-4](DECISIONS.md)).
- **Screens** drawn to scale, any layout; the main screen (★); All good / needs attention.
- **Settings** per screen: on/off, resolution, refresh rate, size 80–200 %, rotation, smooth motion, HDR where supported — only real options.
- **Arrange**: the arrow keys move a screen, the others make room, edges snap, overlaps refused.
- **Brightness** in tens, per screen and for all, through ddcutil (no password).
- **Identify**: one screen dark at a time, "which one?", remembered; **names**.
- **Try (F9)** with a 12-second keep-or-go-back countdown run by an independent process; **Save (F10)** with a plain review and a backup (20 kept).
- **The manual** (M), seven pages.
- **Fixed from Javier's first run:** F-1 typing a name closed the app · F-2 screens stayed dark after Identify · F-3 no manual.
- **After a save, a warning if Sway would not read the file** (the include line missing).
- **Tests: 50, warnings: 0** (first release, so no earlier count to compare).
- **Not tested yet:** one and two screens, 80 / 90 % on real apps, text console — see the README.
