# Start-at-login apps (applet 10)

**What it does:** starts the apps you marked "start at login" — today **Dropbox** and
**Insync** — when you log in to hypeForge. Sway does not do this by itself, so without this
applet they never started.

## How it works

It reads **your** autostart folder, `~/.config/autostart/` (one small file per app), and starts
each app once at login. It skips an app that is already running, one marked hidden, and one
meant only for other desktops. To see what it would start: `hypeforge-autostart --list`.

Apps that keep running in the background then show their icon in the **tray** on the top bar.

## Settings

Add or remove an app: put its `.desktop` file in, or take it out of, `~/.config/autostart/`.
A **Startup apps** Forge app will manage this list for you later.
