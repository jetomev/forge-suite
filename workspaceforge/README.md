<p align="center">
  <img src="../hypeforge/assets/kognogos-emblem.png" alt="KognogOS emblem" width="96">
</p>

<p align="center">
  <img alt="workspaceForge release" src="https://img.shields.io/github/v/release/jetomev/forge-suite?filter=workspaceforge-*&label=release&style=flat-square&labelColor=313244&color=a6e3a1">
  <a href="https://aur.archlinux.org/packages/workspaceforge"><img alt="workspaceForge on the AUR" src="https://img.shields.io/aur/version/workspaceforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1"></a>
  <img alt="Sway" src="https://img.shields.io/badge/for-Sway-89b4fa?style=flat-square&labelColor=313244">
  <img alt="License: GPLv3" src="https://img.shields.io/badge/license-GPLv3-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Built by a human and an AI" src="https://img.shields.io/badge/built%20by-human%20%2B%20AI-f9e2af?style=flat-square&labelColor=313244">
</p>

# workspaceForge

**Your workspaces, in the terminal.** On the KognogOS desktop a workspace covers all your screens at once: Win + 4 takes every screen to Gaming. workspaceForge is where you set them up: their names and order, **which apps open on each one** (however you start them). Without it, all of that lives in a settings file edited by hand; workspaceForge is the friendly way in.

**Made for KognogOS's hypeForge desktop on Sway. A terminal app: any terminal, even a plain text console with no graphical session.** Details in [Where it runs](#where-it-runs).

## What it does

- **Workspaces:** name them, add up to nine for now (Win + 1 … 9), reorder, delete. Deleting one never closes a window; its windows move to a workspace you pick.
- **Apps:** each workspace has a list of the apps that open on it. Steam on Gaming, Spotify on Entertainment. Start an app from the launcher, a terminal or Steam itself, and it opens on its workspace, with your screens following it. Apps on no list open where you are.
- **Sharing** (a screen keeping the same apps across workspaces) is being rethought by Javier and comes back later; the file's sharing is kept as it is.
- **Saves with a review**, a backup first, and applies at once. No logout.

It does **one** job on purpose: where windows sit on a screen and which ones float is a separate Forge app.

## How it looks

| Workspaces | Apps |
|---|---|
| ![Workspaces](docs/images/workspaces.png) | ![Apps](docs/images/apps.png) |

## Where it runs

- **Desktop:** made for **KognogOS's hypeForge desktop on Sway**. It edits the settings of hypeForge's Workspaces helper, which does the switching; without hypeForge there is nothing for it to set up.
- **Terminal:** it is a terminal app. It runs in any terminal window, and also on a **plain text console (a tty) with no graphical session**: there it edits the settings for your next login, but it can't move open windows.
- **Distribution:** written for **KognogOS** (Arch-based) and installed from the AUR (`workspaceforge`). It needs only Python, Textual and forgekit, so it runs on any Linux distribution, but hypeForge itself is only on KognogOS today.

## Install and run

```
yay -S workspaceforge
```

Then `workspaceforge`, or the **Workspaces** page of hypeForge Settings.

## Status

**1.0.0, October 9, 2026.** Workspaces and Apps. **Sharing** is off the menu while Javier rethinks it (D-7), and **nine workspaces** is the most for now (D-6). What changed: [docs/CHANGELOG.md](docs/CHANGELOG.md) · what's next: [docs/ROADMAP.md](docs/ROADMAP.md) · decisions: [docs/DECISIONS.md](docs/DECISIONS.md) · the design: [docs/design/](docs/design/) · tests: [testing/](testing/) · the list: [TODO.md](TODO.md).

## License & credits

GPLv3. Built by Javier and Claude, part of the [Forge Suite](../), on [forgekit](../forgekit/). The work itself is done by hypeForge's Workspaces applet; thanks to the Sway project, whose workspaces and IPC make all of it possible.
