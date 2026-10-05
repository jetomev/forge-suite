# Getting started

**hypeForge** is the KognogOS desktop: a *tiling* desktop, which means windows do not pile up
on top of each other — each one gets its own part of the screen, and they share the space.
It runs on **Sway** and adds small pieces of its own, called **applets**.

## The first keys to know

| Keys | What it does |
|---|---|
| **Win + Space** | The launcher: open apps, lock, log out, reboot, shut down |
| **Win + 1 … 6** | Switch workspace — all three screens together |
| **Alt + F4** | Close a window |
| **Win + F1** | This help, with the full key chart |

*Win* is the Windows key (the one with the logo).

## The applets

Each applet does one job and can be switched on or off on its own. Every one has a small
settings file in `~/.config/hypeforge/applets/`. The **hypeForge Settings** will be the
place to change them; until then the files can be edited by hand.

1. **Workspaces Management** — six workspaces across all three screens
2. **Window Placement** — every new window goes to its spot by itself
3. *Folder Tabs* — coming in the look phase
4. **App Sections** — the launcher, sorted by workspace
5. **Window Rules** — which windows float
6. **Help** — this guide and the key chart

## No title bars

Windows have a thin border and no title bar, so there is no close button to look for:
**Alt + F4** closes, **Win + left mouse button** drags, **Win + right mouse button** resizes.
