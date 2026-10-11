# Getting started

**hypeForge** is the KognogOS desktop: a *tiling* desktop, which means windows do not pile up
on top of each other — each one gets its own part of the screen, and they share the space.
It runs on **Sway** and adds small pieces of its own, called **applets**.

## The first keys to know

| Keys | What it does |
|---|---|
| **Win + Space** | The launcher of your style: open apps (or click the KognogOS emblem) — Start on Windows 11, Kickoff on KDE, the emblem menu on Mac OS 9 |
| **Win + 1 … 6** | Switch workspace — every screen together |
| **Win + W** | The list of workspaces (or click **Workspaces** on the bar) |
| **Win + F** | Your favorite apps (or click **Favorites** on the bar) |
| **Win + O · I · P** | The menu bar's **Window**, **Special** and **Help** menus as lists (the underlined letter) |
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
11. **USB drives** — mounted by themselves; open or eject them from the bar

## The top bar

**Left** (a lighter shade): the **KognogOS emblem** (the launcher), then the menus
**<u>W</u>orkspaces** and **<u>F</u>avorites** — the underlined letter is the key: Win + W, Win + F.

**Centre:** the apps that are open, one icon per window — click to go to it, middle click to
close it.

**Right**, left to right: the **tray** (apps running in the background — Steam, Discord,
Dropbox, Insync…), the **clipboard**, **USB drives**, **Bluetooth**, **network**, **volume** | the **date and
time** | the **bell** and the **⏻ power menu** (Lock · Log Out · Reboot · Shut Down — the last
three ask first).

## No title bars

Windows have a thin border and no title bar, so there is no close button to look for:
**Alt + F4** closes, **Win + left mouse button** drags, **Win + right mouse button** resizes.
