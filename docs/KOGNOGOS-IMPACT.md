# What moving off Plasma changes in KognogOS

*[D-6](DECISIONS.md#d-6--plasma-will-be-replaced): KognogOS moves from KDE Plasma to the hypeForge desktop "little by little". This page lists what that touches, so nothing is forgotten and nothing changes by surprise. **Nothing in KognogOS has changed yet.** On the test desktop, Plasma stays installed until hypeForge works and Javier is fully daily driving it; only then is it taken down. Each item gets its own issue in the [KognogOS repository](https://github.com/jetomev/KognogOS) when its turn comes.*

---

## Carries over unchanged

| Piece | Why it is unaffected |
|---|---|
| **nog and the tiers** | They manage packages, whatever the desktop |
| **The Forge apps** | They run in Alacritty, and they will run in Alacritty under hypeForge too |
| **Alacritty, fish, Tide, the shell greeting** | Terminal tools; the terminal is the centre of the new desktop |
| **Boot splash (Plymouth) and the GRUB theme** | They run before any desktop starts |
| **The login screen's KognogOS theme** | SDDM does not need Plasma; the theme is plain QtQuick |
| **Catppuccin Mocha, the emblem, the wallpapers** | They are the KognogOS look; hypeForge wears them |
| **System identity** (os-release, the self-healing hook) | Independent of the desktop |

## Changes, one at a time

| Piece today | What happens | When |
|---|---|---|
| **All five editions assume Plasma** (`config/profiles.toml`) | Editions are rebuilt on the hypeForge desktop | After hypeForge's first release |
| **`skel/` from `scripts/export-plasma.py`** (Plasma settings copied into every new account) | Replaced by hypeForge's portable folder as the default settings | When the editions switch |
| **The KognogOS splash screen** (`org.kognogos.splash`, a Plasma look-and-feel package) | Retired; the Plymouth boot splash remains | When the editions switch |
| **Plasma lock screen fork** ([KognogOS#3](https://github.com/jetomev/KognogOS/issues/3)) | Becomes unnecessary: the lock screen is the one chosen in the recipe, and it is themeable without forking anything | Revisit once the recipe picks a lock screen |
| **Default apps: Dolphin, Konsole, Kate, Gwenview, Ark, KCalc, Spectacle** | Reviewed against the recipe's lighter and terminal-first choices | Phase 1 choices, then the editions |
| **Tier pins for `kwin` and `plasma-workspace`** | Replaced by the `hyprland-family` group ([D-9](DECISIONS.md#d-9--updates-are-locked-by-us-through-nog)) | With hypeForge's nog lock |
| **Panel launchers and web shortcuts** | Moved to the new launcher and bar | Phase 2 |
| **Which login screen program** (SDDM, or greetd / Ly; this evaluation was already open) | Decided in the recipe | Phase 1 |
| **Public wording**: the KognogOS README, the `kde-plasma` GitHub topic, kognogos.org | Updated when the switch actually lands, not before | The same day it lands |

---

*Found while researching this page (2026-09-28), and not caused by hypeForge: the test desktop's nog uses its own stock tier list, not KognogOS's longer one. So on that desktop `kwin` and `plasma-workspace` wait 7 days, not the 15 KognogOS intends. Whether to fix that is Javier's call.*
