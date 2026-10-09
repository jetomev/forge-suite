<p align="center">
  <img src="../hypeforge/assets/kognogos-emblem.png" alt="KognogOS emblem" width="96">
</p>

<p align="center">
  <img alt="nightForge release" src="https://img.shields.io/github/v/release/jetomev/forge-suite?filter=nightforge-*&label=release&style=flat-square&labelColor=313244&color=a6e3a1">
  <img alt="License: GPLv3" src="https://img.shields.io/badge/license-GPLv3-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Built by a human and an AI" src="https://img.shields.io/badge/built%20by-human%20%2B%20AI-f9e2af?style=flat-square&labelColor=313244">
</p>

# nightForge

**Warmer screens in the evening, your way.** The night light's own app: switch it on or off, choose how warm the evening gets, and when (by the sun at your place, or fixed times). A terminal app, and the Night light page of hypeForge Settings.

> 🖥 **Where it runs:** made for **KognogOS's hypeForge desktop on Sway** (the night light, wlsunset, works on Sway and its wlroots family, not on KDE or GNOME) · **any terminal, even a plain text console**, where it edits the settings for the next login · written for KognogOS; needs Python, Textual, forgekit and wlsunset.

## How it looks

| Night Light | Schedule |
|---|---|
| ![Night Light](docs/images/night-light.png) | ![Schedule](docs/images/schedule.png) |

## Install and run

```
yay -S nightforge
```

Then `nightforge`, the **Night light** page of hypeForge Settings, or the tray icon. At login hypeForge runs `nightforge start`.

## Status

**1.0.0, October 9, 2026.** What changed: [docs/CHANGELOG.md](docs/CHANGELOG.md) · next: [docs/ROADMAP.md](docs/ROADMAP.md) · decisions: [docs/DECISIONS.md](docs/DECISIONS.md) · the design: [docs/design/](docs/design/) · tests: [testing/](testing/) · the list: [TODO.md](TODO.md).

## License & credits

GPLv3. Built by Javier and Claude, part of the [Forge Suite](../), on [forgekit](../forgekit/). The night light itself is [wlsunset](https://sr.ht/~kennylevinsen/wlsunset/) by Kenny Levinsen; the sun times use NOAA's solar calculator formulas. Thank you both.
