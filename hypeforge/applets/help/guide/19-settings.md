# hypeForge Settings — the control centre

**What it does:** one window for every setting of the desktop. A list on the left, with an icon per
page; the chosen page on the right. It opens on **Home**: a card for each part of the system, with
three lines of how it's set up right now (screens, workspaces, network, sound, printer, night light,
passwords, packages, boot menu, terminal).

## How to use it

- Open it from the launcher: **Settings** group → **hypeForge Settings** (the first entry).
- **Home** shows the cards. **Click a card** to open its page: Screens, Passwords, Packages,
  Boot Menu and Terminal have one; the others show what they know until their app exists.
- **Pick a page on the left**: its app opens on the right, with its own menu bar, keys and mouse.
  Click the list to change page; the app you leave keeps running and comes back as you left it.
- The apps here have **no Quit of their own**. **Quit** (last in the list) closes Settings and
  every app inside it; an app with something not saved asks you first, on its own page.
- **Manual, License and About** open on the right too.

## Where it comes from

- The pages: `~/.config/hypeforge/applets/settings.toml` (`name`, `command`, `forge = true` for
  Forge apps, optional `icon`).
- The Home cards: `applets/settings/home.py` in hypeForge — each card asks the system in the
  background, so a slow answer never freezes the window.
