# Notifications and the bell (applet 7)

**What it does:** messages from your apps ("download finished", a new chat message…) pop up at
the **top right of the screen you are using**, just under the bar. They close by themselves
after 5 seconds; urgent ones (red border) stay until you click them. The **bell** on the bar
counts the ones you have not looked at yet.

## How to use it

- **Click a pop-up** to close it; **right click** closes them all.
- **Win + N** closes every pop-up on screen; **Win + Shift + N** brings back the last one closed.
- **The bell:** grey when nothing is new; **yellow with a number** when something is.
  **Click it** to see your recent notifications, under the bar's right end (the number goes away); click again to close
  the list. **Right click** turns **Do Not Disturb** on or off: the bell turns red, pop-ups
  stay hidden, and they are still kept in the list.
- **The clock** (Windows 11, macOS, KDE, COSMIC and the Rice): a click opens your recent
  notifications as cards, with **Clear all**, and the month's calendar under them (‹ › change the month). **Click a day to open
  your calendar on it**: the Calendar app you picked in Default apps (Thunderbird opens on its calendar), or Google
  Calendar in your browser when none is picked.
- **On the Rice** the bell sits right after the time, in the middle of the bar: a click on the
  date, the time or the bell opens that same pop-up (right click on the bell: Do Not Disturb).

## When a part of the desktop breaks

Every piece hypeForge starts at login (the bar, Workspaces, Window Placement, the launcher's sections, the
clipboard…) is watched. If one of them stops with an error, a notification says so at once and stays until you
click it: **"hypeForge: Workspaces stopped"**, the last line of what went wrong, and where its log is
(`~/.local/state/hypeforge/logs/`). Nothing is restarted on its own; logging out and in again starts it fresh.
A style switch or logging out never counts as a crash.

**The bar is the one exception: it comes back by itself.** If the bar disappears, the bar guard starts it
again within a couple of seconds and a notification says **"The bar came back"**. What the bar said last is
kept in `~/.local/state/hypeforge/logs/bar-crashes/` (the last 20, kept across restarts of the computer).
If it keeps stopping (more than five times in five minutes), the guard leaves it down and a notification that
stays says **"The bar keeps stopping"**; logging out and in again starts it fresh.

## Settings

The pop-ups' look, place and timing: `~/.config/mako/config` (mako draws them). A
Notifications Forge app will set all of it later.
