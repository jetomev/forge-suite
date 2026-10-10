<p align="center">
  <img src="hypeforge/assets/kognogos-emblem.png" alt="KognogOS emblem" width="96">
</p>

<p align="center">
  <img alt="Status: growing" src="https://img.shields.io/badge/status-growing-fab387?style=flat-square&labelColor=313244">
  <img alt="Terminal apps first" src="https://img.shields.io/badge/apps-terminal%20first-b4befe?style=flat-square&labelColor=313244">
  <img alt="Catppuccin Mocha" src="https://img.shields.io/badge/theme-Catppuccin%20Mocha-cba6f7?style=flat-square&labelColor=313244">
  <img alt="License: GPLv3" src="https://img.shields.io/badge/license-GPLv3-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Built by a human and an AI" src="https://img.shields.io/badge/built%20by-human%20%2B%20AI-f9e2af?style=flat-square&labelColor=313244">
</p>

# 🧰 Forge Suite

> **The apps of KognogOS, in one place.** KognogOS is **[nog](https://github.com/jetomev/nog)**, its package manager, **plus the Forge Suite**: small apps that set up and run the desktop, most of them in the terminal, all with the same look. This repository holds them, **one section per app** ([D-60](hypeforge/docs/DECISIONS.md)).

---

## The sections

| Section | What it is | Where it runs | Status |
|---|---|---|---|
| **[hypeForge](hypeforge/)** | The KognogOS desktop: a slim, quick tiling desktop on Sway, built from small applets | **Sway** (it is the desktop) · Arch Linux / KognogOS | 🔄 being built, lived in daily |
| **[displayForge](displayforge/)** | Screen settings in the terminal: arrange, resolution, refresh rate, size, rotation, brightness — with a countdown that undoes a change by itself | **Sway only**, in a terminal window · written for KognogOS · on a plain text console it explains why and closes | ✅ ![displayForge on the AUR](https://img.shields.io/aur/version/displayforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) |
| **[sudoForge](sudoforge/)** | The password helper for the Sway desktop: one floating box for every admin request (the system's pop-up, and `sudo -A`), saying who is asking and what for | **Sway only** (its box opens in an Alacritty window) · written for KognogOS · not for a plain text console | ✅ ![sudoForge on the AUR](https://img.shields.io/aur/version/sudoforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) |
| **[workspaceForge](workspaceforge/)** | Your workspaces in the terminal: their names and order, and which apps open on each one, however you start them | made for **hypeForge on Sway** · **any terminal, even a plain text console** · written for KognogOS, needs only Python | ✅ ![workspaceForge on the AUR](https://img.shields.io/aur/version/workspaceforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) |
| **[nightForge](nightforge/)** | The night light, your way: on or off, how warm the evening gets and when (by the sun or fixed times), with its own tray icon (a muted ☀ by day, a mustard ☾ at night) | made for **hypeForge on Sway** (the night light is wlsunset, Sway's wlroots family) · **any terminal, even a plain text console** · written for KognogOS | ✅ ![nightForge on the AUR](https://img.shields.io/aur/version/nightforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) |
| **[forgekit](forgekit/)** | The shared foundation every Forge app is built on: title bar, menu bar, dialogs, one look — the start-up check that explains when an app can't run here (0.7.0), the password's dots centred (0.8.0), every menu entry's keys made from the menu and the `--hypeforge` start option for hypeForge Settings (0.10.0) | **any Linux distribution** (a library) · its apps run in any terminal, with or without a desktop, a plain text console too | ✅ ![forgekit on the AUR](https://img.shields.io/aur/version/python-forgekit?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) |

**Moving in, one at a time** (each keeps its own version, tags `<app>-vX.Y.Z` and AUR package; its old repository is archived with a pointer). **Moved in:** forgekit (2026-10-06, with its full history). **Next:** [alacrittyForge](https://github.com/jetomev/alacrittyforge) ![alacrittyForge on the AUR](https://img.shields.io/aur/version/alacrittyforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) · [bitlaForge](https://github.com/jetomev/bitlaforge) ![bitlaForge on the AUR](https://img.shields.io/aur/version/bitlaforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) · [nogForge](https://github.com/jetomev/nogforge) ![nogForge on the AUR](https://img.shields.io/aur/version/nogforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) · [grubForge](https://github.com/jetomev/grubforge) ![grubForge on the AUR](https://img.shields.io/aur/version/grubforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) (last: it has the most users).

**Staying outside, on purpose:** [nog](https://github.com/jetomev/nog) ![nog on the AUR](https://img.shields.io/aur/version/nog?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) (the heart of KognogOS) and [mindForge](https://github.com/jetomev/mindforge) ![mindForge on the AUR](https://img.shields.io/aur/version/mindforge?label=AUR&style=flat-square&labelColor=313244&color=a6e3a1) (the working agreement between the human and the AI, kept on its own for now).

**Coming, born here:** one Forge app for every setting of the desktop — sound, network, Bluetooth, a theme manager, notifications, workspaces and windows, lock and idle, default and startup apps, USB drives, a calculator — all held by **hypeForge Settings**, the control centre ([D-59](hypeforge/docs/DECISIONS.md)); for installing, **installForge** and **welcomeForge**; later, **fileForge**, **cloneForge**, **greetForge** and **promptForge**. Most names are still to come. The same list is on [kognogos.org](https://kognogos.org/#forge); the detail is in [hypeForge's TODO](hypeforge/TODO.md).

---

## The rule every app follows

1. **Terminal first** — a text-based app wherever one does the job.
2. **Works with Sway** — nothing that brings a whole other desktop along.
3. **Smallest install** — the fewest packages that do the job well.

([D-57](hypeforge/docs/DECISIONS.md)) And every app is built on **[forgekit](forgekit/)**, so they all look and work the same.


---

## How this is built

A human and an AI, working in the open. Decisions are written down the day they are made, each section keeps its own to-do list and decision log, and every commit is GPG-signed. The method: [Building grubForge with AI](https://github.com/jetomev/grubforge/blob/main/docs/AI-COLLABORATION.md).

**jetomev** — idea, vision, direction, testing · **Claude (Anthropic)** — co-developer, architecture, research, implementation

Free software under the **GNU General Public License v3.0** ([LICENSE](LICENSE)).
