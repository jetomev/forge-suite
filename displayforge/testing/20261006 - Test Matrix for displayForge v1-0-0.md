# Test Matrix — displayForge v1.0.0

*2026-10-06 · the KognogOS test desktop: NVIDIA RTX 3060, three Sceptre Y27 (2560 × 1440, 144 Hz), Sway 1.12. Results: [Test Results](20261006%20-%20Test%20Results%20for%20displayForge%20v1-0-0.md).*

| # | What | How | Who |
|---|---|---|---|
| 1 | Opens from the launcher, floating | Win + Space → "display" | Javier |
| 2 | Screens drawn as they sit; ★ on the main one | 1 · Screens | Javier |
| 3 | A change is tried, kept | 2 · Settings → refresh 120 Hz → F9 → Keep it | Javier |
| 4 | A change goes back on request | same → Go back now | Javier |
| 5 | A change goes back **by itself** | same → touch nothing for 12 s | Javier |
| 6 | Save writes the file, with a backup | F10 → review → Save | Javier |
| 7 | Identify: one screen dark at a time, answered, remembered, **brightness restored** | 5 · Start | Javier |
| 8 | Brightness per screen and for all | 4 · Brightness | Javier |
| 9 | Names typed and shown | 5 · Identify → names | Javier |
| 10 | Arrange: arrows move a screen, others make room, no overlaps | 3 · Arrange | Javier |
| 11 | The manual | M, Help → Manual | Javier |
| 12 | Automatic tests | `python3 -W default -m unittest tests.test_screens tests.test_engine tests.test_app` | Claude |
| 13 | One and two screens | test VM | Claude |
| 14 | Sizes 80 / 90 % on real apps | test VM | Claude |
| 15 | Plain text console, 100 columns | TTY | Claude |
