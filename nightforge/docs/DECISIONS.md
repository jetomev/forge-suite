# nightForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

## 2026-10-25

### D-8 · On any hypeForge bar the tray icon steps aside: the night light is in Quick Settings (Javier)
*"now we can remove the night light icon, outside the quick settings from all themes. Let's keep using the quick settings combo on all."* hypeForge D-117 took the moon off every style's bar; the night light lives in Quick Settings (its tile opens the Night light page, with nightForge at the bottom right). D-7 hid the icon only where the moon was, so it would have come back everywhere. Now it hides wherever the bar is hypeForge's (every bar file hypeforge-theme writes starts with `// hypeForge`) and still shows on any other bar. #129.

## 2026-10-11

### D-7 · The tray icon steps aside where the bar has its own moon (Javier)
*"in rice, now I have 2 night-light icons. Take the old one please, leave the one with the window and the slider."* hypeForge's Rice has a night-light moon on its bar (hypeForge D-89) that opens the pop-up with the slider; the tray icon was the same button twice. A bar can't hide one app's tray icon, so nightForge does it: when hypeForge's bar in use (`~/.config/sway/waybar/config.jsonc`) places `custom/nightlight`, the icon's status is **Passive**, which Waybar's tray hides; on a style without the moon it's **Active** again. It watches the bar's folder, so a style switch shows or hides it at once (`NewStatus`). Tested on the private bus with the Rice's and Windows 11's real bar files (fails on 1.0's code), and live: the yellow tray moon gone, the bar's moon kept. Issue forge-suite #82.

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
