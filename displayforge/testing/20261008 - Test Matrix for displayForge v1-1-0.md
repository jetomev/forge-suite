# Test Matrix — displayForge v1.1.0

*2026-10-08 · the KognogOS test desktop: NVIDIA RTX 3060, three Sceptre Y27 (2560 × 1440, 144 Hz), Sway. From Javier's run inside hypeForge Settings ([F-4 #50](https://github.com/jetomev/forge-suite/issues/50), [F-5 #51](https://github.com/jetomev/forge-suite/issues/51)). Runs on forgekit 0.10.0. Results go in a Test Results file next to this one.*

| # | What | How | Who | Result |
|---|---|---|---|---|
| 1 | Every underlined letter is a shortcut | Ctrl+S, Ctrl+E, Ctrl+A, Ctrl+B, Ctrl+I, Ctrl+H, from every page | Javier | |
| 2 | The numbers follow the menu, Help is 6 | 1 … 5 go to the pages, 6 opens Help's menu | Javier | |
| 3 | Bottom bar says "1-6 menu" | look at the bottom row on each page | Javier | |
| 4 | Try (F9) and Save (F10) only where things change | the bottom row shows F9 / F10 on Settings and Arrange, not on Screens, Brightness, Identify | Javier | |
| 5 | A reminder elsewhere | change a setting, go to Brightness: the bar says the changes wait in Settings (2) or Arrange (3); F9 there only reminds | Javier | |
| 6 | Quit asks, No | change a setting → Q → "Apply your changes before quitting?" → No: it quits, the screens unchanged | Javier | |
| 7 | Quit asks, Esc | same → Esc: stays, the change still waiting | Javier | |
| 8 | Quit asks, Yes | same → Yes → the countdown → Keep It → the save review → Save: quits, the change saved | Javier | |
| 9 | Kept but not saved is asked too | change → F9 → Keep It → Q: the question comes up | Javier | |
| 10 | The Save button in the bar | change → F9 → Keep It → click Save (F10) in the bar: the review opens | Javier | |
| 11 | Button labels | Try It (F9), Save (F10), Keep It (Enter), Go Back Now (Esc), None of Them, Dim It Again | Javier | |
| 12 | Inside hypeForge Settings: no Quit | Settings → Screens: no Quit in the bar; Q and Ctrl+Q do nothing | Javier | |
| 13 | Inside Settings: quitting Settings asks | change a setting in Screens → Settings' Quit: Settings shows the Screens page and displayForge asks its question | Javier | |
| 14 | Tab and Enter still work | Settings page: Tab moves between fields, Enter chooses (Ctrl+I is not Tab) | Javier | |
| 15 | Automatic tests | `PYTHONPATH=../forgekit python -W always -m unittest discover -s tests`: 63 pass, 0 warnings | Claude | ✅ 2026-10-08 |
