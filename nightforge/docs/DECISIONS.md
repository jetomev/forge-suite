# nightForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

## 2026-10-09

### D-6 · A click on the tray icon shows the menu; nothing opens the app by itself (Javier)
His run: *"the tray icon works. right click opens the app. I wouldn't. just left click and menu."* The icon says it is a menu (`ItemIsMenu`), so the bar opens the menu on a click; Activate does nothing. "Open nightForge…" stays in the menu.

### D-5 · The tray icon's colours (Javier)
*"The tray icon.... muted during the day, mustard color when night light activates.... eh! eh! eh!"* By day a muted grey-blue sun (Catppuccin's subtext, 166 173 200); while warm a mustard moon (225 173 1); off a dim ring (108 112 134).

### D-4 · A tray icon, nightForge's own (Javier)
Approving the design: *"This app have to come with a tray icon as well, btw."* A real tray icon (StatusNotifierItem) in the bar's tray, next to other apps' icons, owned by nightForge (`nightforge tray`), so it works on any bar with a tray, not just hypeForge's. Always there: ☀ by day, ☾ while warm, ○ when switched off. Its menu: Automatic · Warm Now · Daylight Now · Turn Off / Turn On · Open nightForge. It replaces the first draft's bar button (question 7). Started with the night light at login. Claude's reading of "tray icon", told to Javier with the choice to change it.

### D-3 · The design is approved (Javier)
*"perfect."* The ten questions go with the recommendations: the name nightForge; off means off now and at every login; Right now holds until Automatic or logout; five warmth steps 3000–5000 K plus a typed number (1000–6500); daytime stays 6500 K; the place as two numbers, nothing looked up online, or fixed times with a fade; nightForge starts the night light at login (`nightforge start`) and restarts it on save; the Night light page of hypeForge Settings; 0.1.0 → 1.0.0 after Javier's run, then the AUR after his install test.

### D-2 · Preview and Save work the same way: pop-ups (Javier, first review)
*"Preview and save has to be the same screen, either both are a popup, or a change on the screen. I would say then popup for both."* Save becomes a review window over the page, like Preview.

### D-1 · nightForge is next (Javier)
Picked from the ranked list after workspaceForge 1.0: *"nightForge it is"* — the smallest whole app on the list (the night light already runs; the Settings Home page already has its card). From his issue #44 (2026-10-07): *"Night-Light → needs its own app to be able to activate/deactivate, modify its settings, etc. … nightForge… I guess."* A new Forge Suite section; the design first, for his approval.
