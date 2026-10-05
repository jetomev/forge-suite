<p align="center">
  <img src="assets/banner.svg" alt="hypeForge — the KognogOS desktop: Sway tiling, terminal apps first, every setting a Forge app" width="100%">
</p>

<p align="center">
  <img alt="Status: building on Sway" src="https://img.shields.io/badge/status-building%20on%20Sway-fab387?style=flat-square&labelColor=313244">
  <img alt="Sway 1.12" src="https://img.shields.io/badge/Sway-1.12-89b4fa?style=flat-square&labelColor=313244">
  <img alt="Terminal apps first" src="https://img.shields.io/badge/apps-terminal%20first-b4befe?style=flat-square&labelColor=313244">
  <img alt="Any Arch Linux install" src="https://img.shields.io/badge/Arch%20Linux-any%20install-94e2d5?style=flat-square&labelColor=313244">
  <img alt="Catppuccin Mocha" src="https://img.shields.io/badge/theme-Catppuccin%20Mocha-cba6f7?style=flat-square&labelColor=313244">
  <img alt="License: GPLv3" src="https://img.shields.io/badge/license-GPLv3-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Built by a human and an AI" src="https://img.shields.io/badge/built%20by-human%20%2B%20AI-f9e2af?style=flat-square&labelColor=313244">
</p>

# ⚡ hypeForge

> **The KognogOS desktop: slim, quick, low on memory.** hypeForge turns any Arch Linux install into a **tiling** desktop on **[Sway](https://swaywm.org)**: windows arrange themselves side by side instead of piling up, all your screens move together as one, and **terminal apps come first**. Every feature is a small piece of its own, and every setting will have its own **Forge Suite app**, all opened from one control centre: **hypeForge Settings**.

> 🚧 **Being built, and lived in.** Since 4 October 2026 hypeForge runs as its own login on the KognogOS test desktop, next to the old desktop, and Javier works in it every day. There is no app to install yet. Follow along in [Issues](https://github.com/jetomev/hypeforge/issues), the [to-do list](TODO.md) and the [decision log](docs/DECISIONS.md).

> 🛡 **Security.** Every commit is GPG-signed and GitHub-Verified, and releases will be signed like the rest of the Forge Suite. **[Where We Stand](https://github.com/jetomev/KognogOS/blob/main/docs/where-we-stand.md)** explains why.

---

## Why hypeForge?

A full desktop like KDE Plasma does everything for you, and it carries a lot of weight to do it. KognogOS started on Plasma. **KognogOS will ship with hypeForge only** ([D-56](docs/DECISIONS.md)).

**Sway** is a *tiling window manager*: the program that draws your windows and places them for you, side by side, so nothing hides behind anything else. It is fast, stable, light on memory and works well on NVIDIA. On its own, though, it is a bare screen: no top bar, no launcher, no lock screen. hypeForge builds the rest, one small piece at a time, under one rule ([D-57](docs/DECISIONS.md)):

| | The rule | In plain words |
|---|---|---|
| 1 | **Terminal first** | If a job can be done by a terminal app (a text-based app), that is the one we use. |
| 2 | **Works with Sway** | Sway's own tools first; nothing that brings a whole other desktop along with it. |
| 3 | **Smallest install** | The fewest packages and the smallest download that do the job well. |

---

## What works today

| Piece | What it does |
|---|---|
| **Workspaces** | Six workspaces (Daily, Work, Entertainment, Gaming, Monitoring, Settings). **Win + 1…6**, or a click on the top bar, switches every screen together. A screen can also keep one space for several workspaces, so its apps stay put. |
| **Window placement** | Every new window goes to the next spot of a fixed order across your screens, then becomes a tab. |
| **Launcher** (Win + Space) | Your favourites first, then the workspaces as sections: an app picked from "Work" opens in Work. Lock, log out, reboot and shut down at the bottom (they ask first). |
| **Window rules** | Small tools (the calculator, settings windows, picture-in-picture video) float above the tiled windows. |
| **Help & Keys** (Win + F1) | A small Forge app with tabs: the key chart and a plain-words guide to every piece. The chart is checked against Sway's real keys before every change is saved. |
| **Lock screen** (Win + Escape) | A big clock and a password box over the blurred KognogOS wallpaper. Locks by itself after 30 minutes; the screens turn off after 60. |
| **Top bar** | The six workspaces, always shown and clickable, and the clock. |
| **Terminal apps** | Alacritty for the terminal, Midnight Commander for files, Fresh for text, numbat for sums, cliamp for music (from the media server). |

The look is **Catppuccin Mocha** with the KognogOS wallpaper: thin borders, no title bars, windows that share a space become tabs, 10 px between windows.

---

## Keys

| Keys | What happens |
|---|---|
| **Win + Space** | The launcher |
| **Win + Enter** | A terminal |
| **Win + 1 … 6** | Switch every screen to that workspace |
| **Win + Shift + 1 … 6** | Send the window to that workspace |
| **Win + arrows** | Move between windows (also across screens); add **Shift** to move the window |
| **Win + W / S / E** | Tabs · stacked · side by side |
| **Win + F** | Full screen |
| **Win + Shift + Space** | Float the window, or put it back in its spot |
| **Alt + F4** | Close the window |
| **Win + Escape** | Lock the screen |
| **Win + F1** | Help & Keys: every key, and the guide |

*The Win key is the one Plasma calls "Meta". The full chart lives in [`applets/help/keys.toml`](applets/help/keys.toml) and in Win + F1.*

---

## How it fits together

1. **The pieces.** Each feature (workspaces, placement, launcher, rules, help, lock…) is its own small piece ([D-47](docs/DECISIONS.md)), with its own settings file in `~/.config/hypeforge/applets/`.
2. **A Forge app for every setting.** Everything that today can only be set up by editing a file gets its own **Forge Suite app**: our own pieces, and outside programs like the music player, the top bar and the launcher's look ([D-59](docs/DECISIONS.md)). Each is a full app that also runs on its own, built on [forgekit](https://github.com/jetomev/forgekit) so they all look and work the same.
3. **hypeForge Settings, the control centre.** One window, like KDE's System Settings: the list on the left, and the chosen Forge app running on the right. Replace one app and nothing else has to change.
4. **nog** installs everything and decides when it updates, and system changes are made only through the apps, never by hand.

The Forge apps already shipped, [grubForge](https://github.com/jetomev/grubforge) and [alacrittyForge](https://github.com/jetomev/alacrittyforge), will be opened from hypeForge Settings too. The full list of upcoming apps is in the [to-do list](TODO.md).

---

## Built for KognogOS, works on any Arch

hypeForge becomes **the KognogOS desktop**, and KognogOS will ship with it alone. What moving off Plasma changes is tracked in the open ([KOGNOGOS-IMPACT](docs/KOGNOGOS-IMPACT.md)). Some things carry over unchanged: nog and its tiers, the Forge apps, Alacritty with fish, the boot splash, the GRUB theme and the Catppuccin look. It is also meant for **any Arch Linux install**.

---

## With thanks

hypeForge is built on other people's work, and we are grateful for it.

- The **[Sway](https://swaywm.org)** team and the wlroots developers, for the ground everything stands on.
- **Every developer whose app hypeForge uses**: Waybar, fuzzel, gtklock, swayidle, swaybg, Alacritty, Midnight Commander, Fresh, numbat, cliamp, and all the others.
- [**Omarchy**](https://github.com/basecamp/omarchy), by DHH and Basecamp, and the **Hyprland** and [**Noctalia**](https://github.com/noctalia-dev/noctalia) teams, whose work taught us a great deal in hypeForge's first attempt.
- The [**Catppuccin**](https://catppuccin.com) team, for the colours everything wears.

We don't compare ourselves with anyone. Our picks are simply our picks.

---

## Roadmap

| Step | What happens | Status |
|---|---|---|
| **Choose the base** | Research, then **Sway** chosen ([D-45](docs/DECISIONS.md)); runs on the test desktop | ✅ |
| **The jobs, one by one** | Workspaces, placement, launcher, rules, help, lock screen ✅ · next: notifications, screenshots, sound and network, the password pop-up | 🔄 in progress |
| **Our own look** | Folder-style tabs, our own top bar, a palette from the KognogOS brand | ⬜ |
| **The Forge apps** | One Forge Suite app per setting, and **hypeForge Settings** to hold them all. Screens, workspaces and window placement become **flexible for any number of screens**, from one to six or more | ⬜ |
| **The first KognogOS release** | KognogOS ships with hypeForge as its only desktop | ⬜ |

Full detail: [docs/ROADMAP.md](docs/ROADMAP.md) · History: [docs/CHANGELOG.md](docs/CHANGELOG.md)

> **The first attempt** (28 Sep – 3 Oct 2026) built a floating Hyprland desktop with Noctalia. It worked, and it was not *us*, so on 4 October Javier started again ([D-44](docs/DECISIONS.md)). Everything from it stays in the [decision log](docs/DECISIONS.md), [RECIPE](docs/RECIPE.md) and [`desktop/`](desktop/) as history and material.

---

## Testing

Every step is tested on the KognogOS test desktop first, where Javier lives in it daily: an NVIDIA RTX 3060 driving three 1440p screens at 144 Hz. That is one setup among many: hypeForge is meant for **one screen or many**, and the screen setups people really use (one, two, four, six…) will be tested as the screen and workspace apps are built. Each finding gets a number (F-1, F-2…) and an [issue](https://github.com/jetomev/hypeforge/issues). Test plans and results are published in [`testing/`](testing/). Virtual machines (a KognogOS install, a plain Arch install) follow before any release.

---

## Documentation

| Document | What's in it |
|---|---|
| [DECISIONS](docs/DECISIONS.md) | Every decision, dated, with who made it and why |
| [TODO](TODO.md) | What is done and what comes next, step by step |
| [DESIGN](docs/DESIGN.md) | How it works (written for the first attempt; being brought up to date) |
| [RECIPE](docs/RECIPE.md) | The options for every job, with sources |
| [KOGNOGOS-IMPACT](docs/KOGNOGOS-IMPACT.md) | What moving off Plasma changes in KognogOS |
| [Research notes](docs/research/) | What was checked, how, and the sources |
| [ROADMAP](docs/ROADMAP.md) · [CHANGELOG](docs/CHANGELOG.md) | Where it's going; where it's been |
| [testing/](testing/) | Every test plan and its results |

---

## How this project is built

hypeForge is a human and AI collaboration. Decisions are written down the day they're made, the to-do list ([TODO.md](TODO.md)) is the handoff between work sessions, and nothing important is trusted to anyone's memory, human or AI. The method is described in [Building grubForge with AI](https://github.com/jetomev/grubforge/blob/main/docs/AI-COLLABORATION.md).

---

## Related Projects

- **[KognogOS](https://github.com/jetomev/KognogOS)** — the distribution hypeForge becomes the desktop of
- **[nog](https://github.com/jetomev/nog)** — tier-aware package manager
- **[forgekit](https://github.com/jetomev/forgekit)** — the shared foundation for the Forge apps
- **[grubForge](https://github.com/jetomev/grubforge)** — bootloader manager
- **[alacrittyForge](https://github.com/jetomev/alacrittyforge)** — terminal configurator
- **[bitlaForge](https://github.com/jetomev/bitlaforge)** — solo Bitcoin mining, honestly framed
- **[mindForge](https://github.com/jetomev/mindforge)** — a working agreement with an AI assistant that doesn't decay

---

## Authors

**jetomev** — idea, vision, direction, testing

**Claude (Anthropic)** — co-developer, architecture, research, implementation

Built as a collaboration between a human with a clear picture of the desktop he wants and an AI that helps build it, one decision at a time.

---

## License

hypeForge is free software, released under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for the full text. Anything we adapt from another project keeps that project's notice.

---

## Contributing

hypeForge is being built in the open, and ideas and experience are welcome. Open an issue. It is especially useful to hear from people running **Sway on NVIDIA**, **Sway across several screens**, or a **light, terminal-first desktop** they love.

If the idea interests you, a star helps others find it.
