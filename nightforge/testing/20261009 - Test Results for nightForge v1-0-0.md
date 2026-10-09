# nightForge v1.0.0 — Test Results (9 Oct 2026)

On the test desktop (Arch, Sway 1.12, hypeForge, three screens).

| Area | Result |
|---|---|
| Automated | **23 PASS**, 0 warnings. 10 behaviours broken on purpose (two nudges for Warm Now, the old one stopped first, off stays off, a failed start says why, warmth below daylight, the backup, Preview goes back by itself, Save is a pop-up review, the tray's Turn Off is saved, the tray registers): **10 caught** |
| Tray, private bus | registers with a stand-in tray host; three pictures; the menu; Warm Now = restart + two nudges; Turn Off saved and shown; a click shows the menu (`ItemIsMenu`) |
| Hidden bench | `scripts/bench-start.py`: the real wlsunset (renamed, so the desktop's is never matched) on a screen-less Sway with a private bus: takes over hypeForge's old line, one night light and one tray, a second start doubles nothing, Warm / Daylight / Automatic / Off / On — **14 of 14**; the desktop's night light untouched |
| Live, 17:40 | `nightforge start` took over the desktop's night light (one wlsunset) and the tray icon registered next to Insync's |
| Javier's run | *"the tray icon works … Tried the options and they work. The app works as well."* Schedule's stray lines → fixed. *"just left click and menu"* → D-6, fixed and restarted live |
| Tonight | sunset ≈ 19:00: the screens warm by themselves, the icon turns mustard — **(filled in at release)** |
| Not tried | one or two screens (a VM); a real text console |
