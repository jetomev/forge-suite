# Night light

**What it does:** after sunset the screens turn a little warmer (less blue), and at sunrise they
go back to normal. Easier on the eyes in the evening; no effect on screenshots or on what
you share.

## nightForge

The night light has its own app, **nightForge**: Settings → **Night light**, the launcher
(Settings → nightForge), or its **tray icon** on the bar.

- **The tray icon:** a muted **☀** by day, a mustard **☾** while the screens are warm, a dim
  **○** when it's off. A click shows its menu: Automatic · Warm Now · Daylight Now ·
  Turn Off / Turn On · Open nightForge.
- **Night Light** page: on or off (at once, and at every login), **Right now** (Automatic, Warm
  Now, Daylight Now: they hold until you pick Automatic again, or log out), the **evening
  warmth** (3000 very warm … 5000 just a touch) with a 10-second **Preview**.
- **Schedule** page: **by the sun at your place** (two numbers, worked out on this computer;
  nothing is looked up online) or **fixed times** with a fade.
- **F10** saves, with a review first; the night light restarts with it at once.

**On the Rice**, a **moon** of its own sits on the bar, just right of the tray (Javier, 10-11):
mustard while the screens are warm, quiet by day, red when switched off. A click opens the Night
light page — the switch, what it's doing in words, the evening warmth, Warm now and Automatic, and
nightForge as the icon at the bottom right. The same page opens from Quick Settings (click its tile). nightForge's
tray icon is still there too, for now; a nightForge update will hide it where the bar has the moon.

## How it works

At login hypeForge runs `nightforge start`: it starts **wlsunset** the way nightForge's
settings say (`~/.config/nightforge/settings.toml`), and the tray icon. `nightforge status` in a
terminal says what it is doing now.

- Not installed yet? `nog install wlsunset` (nightForge needs it to warm the screens).
