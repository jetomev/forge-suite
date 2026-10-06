# Getting started

**hypeForge** is the KognogOS desktop: a *tiling* desktop, which means windows do not pile up
on top of each other — each one gets its own part of the screen, and they share the space.
It runs on **Sway** and adds small pieces of its own, called **applets**.

## The first keys to know

| Keys | What it does |
|---|---|
| **Win + Space** | The launcher: open apps, lock, log out, reboot, shut down (or click the KognogOS emblem) |
| **Win + 1 … 6** | Switch workspace — every screen together |
| **Win + W** | The list of workspaces (or click **Workspaces** on the bar) |
| **Win + F** | Your favorite apps (or click **Favorites** on the bar) |
| **Alt + F4** | Close a window |
| **Win + Escape** | Lock the screen |
| **Print Screen** | Screenshot: drag a box |
| **Win + C** | The clipboard history |
| **Win + N** | Close the notifications on screen |
| **Win + F1** | This help, with the full key chart |

*Win* is the Windows key (the one with the logo).

## The applets

Each applet does one job and can be switched on or off on its own. Every one has a small
settings file in `~/.config/hypeforge/applets/`. The **hypeForge Settings** will be the
place to change them; until then the files can be edited by hand.

1. **Workspaces Management** — six workspaces across all your screens
2. **Window Placement** — every new window goes to its spot by itself
3. *Folder Tabs* — coming in the look phase
4. **App Sections** — the launcher, sorted by workspace
5. **Window Rules** — which windows float
6. **Help** — this guide and the key chart
7. **Notifications** — the bell on the bar, Do Not Disturb
8. **Screenshots** — Print Screen, saved, copied, ready to draw on
9. **Clipboard** — the history of what you copied
10. **Start-at-login apps** — starts the apps in your autostart folder (Sway does not by itself)

## The top bar

From the left — on a slightly lighter background — the **KognogOS emblem** (the launcher),
the menus **Workspaces** and **Favorites** (the underlined letter is the key: Win + W, Win + F).
On the right, on the same shade: the **tray** (apps running in the
background — Steam, Discord, Dropbox, Insync…: click to open, right click for their menu), the
**clipboard icon**, the **bell**, a thin line, and the date and time.

## No title bars

Windows have a thin border and no title bar, so there is no close button to look for:
**Alt + F4** closes, **Win + left mouse button** drags, **Win + right mouse button** resizes.
