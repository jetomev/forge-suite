<p align="center">
  <img src="../hypeforge/assets/kognogos-emblem.png" alt="KognogOS emblem" width="96">
</p>

<p align="center">
  <img alt="Version 1.0.1" src="https://img.shields.io/badge/version-1.0.1-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Sway" src="https://img.shields.io/badge/for-Sway-89b4fa?style=flat-square&labelColor=313244">
  <img alt="Terminal app" src="https://img.shields.io/badge/app-terminal-b4befe?style=flat-square&labelColor=313244">
  <img alt="Tests: 54" src="https://img.shields.io/badge/tests-54-94e2d5?style=flat-square&labelColor=313244">
  <img alt="License: GPLv3" src="https://img.shields.io/badge/license-GPLv3-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Built by a human and an AI" src="https://img.shields.io/badge/built%20by-human%20%2B%20AI-f9e2af?style=flat-square&labelColor=313244">
</p>

# 🖥 displayForge

> **Screen settings for the KognogOS desktop, in the terminal.** Arrange your screens, pick the resolution and refresh rate, make things bigger or smaller, rotate a screen, switch one off, set the brightness, and give your screens names. Every change comes with a **safety countdown**: if a change leaves you staring at a black screen, it goes back by itself. Part of the **[Forge Suite](../README.md)**, made for **[hypeForge](../hypeforge/README.md)**. **Works on Sway only**, and says so at launch anywhere else.

> 🛡 **Security.** Every commit is GPG-signed and GitHub-Verified. displayForge needs no password: it only writes your own files, with a backup first.

<p align="center"><img src="docs/images/screens.png" alt="displayForge's Screens view: three screens drawn side by side, the middle one marked as the main screen" width="90%"></p>

---

## What it does

| View | What you do there |
|---|---|
| **1 · Screens** | See your screens drawn **as they sit on your desk**, to scale, any layout. The ★ is the main screen, where your workspaces start. A green **All good**, or a list of what needs attention. |
| **2 · Settings** | Per screen: on or off, resolution, refresh rate, size of things (80 % – 200 %), rotation, smooth motion (adaptive sync), HDR where the screen has it. **Only what your screen really supports is offered.** |
| **3 · Arrange** | Move a screen with the arrow keys; the others make room and the edges snap together. Side by side, one above another, three over three: any layout. |
| **4 · Brightness** | Each screen, or all of them, in steps of ten. Changes at once; the screens keep it themselves. |
| **5 · Identify** | Same-model screens look identical to the computer. Each one goes dark for three seconds, you say which it was, and displayForge remembers. Name your screens here too. |

## The three steps for a change

1. **Change** something. Nothing happens on your screens yet.
2. **Try it (F9).** The change appears, and a window asks **"Keep these settings?"** with a 12-second countdown. Do nothing and it **goes back by itself** — and that countdown runs outside displayForge, so it happens even if displayForge closes.
3. **Save (F10)** to keep it after your next login. A review of every change first, and a backup of the old file.

<p align="center"><img src="docs/images/keep-or-go-back.png" alt="The Keep these settings window, going back in 12 seconds unless kept" width="90%"></p>

<details><summary>More pictures: Settings, Arrange, Brightness</summary>

<p align="center"><img src="docs/images/settings.png" alt="Settings for one screen" width="90%"></p>
<p align="center"><img src="docs/images/arrange.png" alt="Arrange: moving a screen with the arrow keys" width="90%"></p>
<p align="center"><img src="docs/images/brightness.png" alt="Brightness for each screen and all screens" width="90%"></p>
</details>

---

## Install and run

displayForge is not packaged yet; it runs from this repository.

- **Sway only.** displayForge sets up screens by talking to Sway, and only Sway. It checks at launch *(1.0.1)*: on any other desktop (KDE, GNOME, Hyprland…) or on a text console it shows one plain screen — what it needs, what it found instead, why, what to use — and closes. Nothing is touched.
- **Needs:** Sway, Python 3.11 or newer, [forgekit](../forgekit/) 0.7.0 or newer (`python-forgekit` in the AUR) and `ddcutil` (for brightness; your screens need **DDC/CI** switched on in their own menu). Without `ddcutil` the launch screen says so and lets you continue; Brightness and Identify are the two views that need it.
- **Run:** `python3 displayforge/main.py` from the Forge Suite folder. In hypeForge it's in the launcher (Win + Space → "display"), opening in its own floating window.
- **Sway must read the saved file:** hypeForge's Sway settings include the line `include ~/.config/sway/outputs` after its own screen lines. displayForge warns you if that line is missing.

## Keys

| Keys | What happens |
|---|---|
| **1 – 5** | The views (or the underlined letter in the menu) |
| **← →** | Pick a screen (Screens, Settings) |
| **Tab** + **arrows** | Arrange: pick a screen, then move it |
| **F9** · **F10** | Try the changes · save them |
| **M** · **?** | The manual · every key |
| **Q** | Quit (asks first if something isn't saved) |

## Where things are kept

| What | Where |
|---|---|
| Your saved screens | `~/.config/sway/outputs` — Sway reads it at every login |
| Backups (the last 20) | `~/.config/displayforge/backups/` |
| Names, and which brightness control is which screen | `~/.config/displayforge/screens.toml` |

---

## Known limits in 1.0.1

Said plainly, so nobody finds out the hard way:
- **Tested on one setup:** three identical 1440p screens on NVIDIA. One- and two-screen setups, the 80 / 90 % sizes on real apps and a plain text console are **not tested yet**; they come next, and anything they find becomes a 1.0.x fix.
- **Arrange** is still being tried by Javier on the real screens.
- No profiles yet (a layout that switches by itself when a screen is plugged in), and no night light.

---

## Roadmap

| Version | What | Status |
|---|---|---|
| **1.0.x** | The tests above: 1 and 2 screens, 80 / 90 %, text console; Javier's Arrange run | ⬜ next |
| **1.0.1** | Sway only, said everywhere and checked at launch (on forgekit 0.7.0's start-up check) | ✅ 2026-10-06 |
| **1.1** | Profiles · a page in hypeForge Settings · an AUR package | ⬜ |
| **1.0.0** | Screens, Settings, Arrange, Brightness, Identify, names; try with a countdown, save with a backup; the manual | ✅ 2026-10-06 |

Full detail: [docs/ROADMAP.md](docs/ROADMAP.md) · History: [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

## Documentation

| Document | What's in it |
|---|---|
| [DECISIONS](docs/DECISIONS.md) | Every decision, dated, who made it and why |
| [TODO](TODO.md) | What is done and what comes next |
| [Design](docs/design/) | The screen drawings Javier approved before any code |
| [Research](docs/research/2026-10-05-displayforge.md) | Sway's screen settings, brightness without a password, why identical screens need Identify |
| [testing/](testing/) | The test plan and results for every version |
| The manual | Inside the app: **M** |

---

## How this project is built

displayForge is a human and AI collaboration. The design was drawn and approved screen by screen before a line of code; decisions are written down the day they're made; every finding from a real run is numbered, fixed, and turned into a test so it can't come back.

**jetomev** — idea, direction, testing · **Claude (Anthropic)** — co-developer, design, implementation

## With thanks

To the **[Sway](https://swaywm.org)** team, whose `output` commands do the real work; to **[ddcutil](https://www.ddcutil.com)** by Sanford Rockowitz, which talks to the screens; to **[Textual](https://textual.textualize.io)**; and to **[Catppuccin](https://catppuccin.com)** for the colours.

## License

Free software under the **GNU General Public License v3.0** — see [LICENSE](../LICENSE).
