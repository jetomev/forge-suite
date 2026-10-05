# Research: which tiling base to restart hypeForge on

*2026-10-04 · for hypeForge (decision D-44) · this desktop: NVIDIA RTX 3060 on driver 615.71.09 (`nvidia-open-dkms`), three identical 2560x1440 screens at 144 Hz, World of Warcraft through Wine, Chrome, Discord, Alacritty, SDDM login, Plasma as the fallback*

**Why this exists.** Javier wants to start the desktop again from a bare *tiling* base (a "tiling window manager" arranges windows side by side automatically, like tiles, instead of piling them on top of each other) and then add one piece at a time, preferring terminal apps. He likes how Hyprland looks but asked whether something **more mature and proven** exists. This page compares the candidates he named (Hyprland, Sway, i3, dwm) plus the ones the community recommends in 2026 (niri, river, and a few others), and recommends one.

**Nothing was installed and nothing was changed on this computer.** Package versions below were read from this computer's package lists (`pacman -Si`) on 2026-10-04; the graphics driver version was read with `nvidia-smi`. Everything else comes from the linked web sources.

**Two words used throughout:**
- **Wayland** is the modern way Linux draws windows on the screen. **X11** (also called **Xorg**) is the old way, from 1987. A *Wayland compositor* is the program that draws everything; on Wayland the window manager and the compositor are the same program.
- **Explicit sync** is a newer way for the graphics card and the desktop to agree when a picture is finished. NVIDIA's driver needs it on Wayland; without it you can get flicker, stutter or half-drawn frames, especially in games.

---

## The short answer

1. **Top pick: Sway.** The most mature and proven tiling base on Wayland: ten years old, at version 1.12 (May 2026), in Arch's official repos, a plain-text settings file whose format has barely changed in years, and the largest set of terminal-friendly companion tools. It has had explicit sync since 1.11 (June 2025), which is what NVIDIA needed. The one wart: it must be started with a flag, `--unsupported-gpu`, because its developers refuse to *call* NVIDIA's closed driver supported. That is a policy statement, not a missing feature.
2. **Runner-up: niri.** The community favourite of 2025–2026, stable, good-looking out of the box (blur since April 2026), in Arch's official repos. It is held back from first place by two things: it is **only three years old with one main developer**, and it **does not yet have explicit sync** (two pull requests are still open as of September 2026), which matters on NVIDIA with three 144 Hz screens and gaming. Its "scrolling" layout is also a different way of working, not classic tiling.
3. **Keep Hyprland only if looks beat calm.** It is the prettiest and handles NVIDIA gaming well, but it is exactly what Javier is moving away from: fast changes that break settings (a whole new Lua settings format arrived in 0.55), and the crashes and bugs we hit.
4. **i3 (X11) is the safety net, not the base.** The most proven tiling window manager of all, and NVIDIA's oldest, best-tested path. But it lives on X11, which the rest of Linux is leaving: **Plasma 6.8 (this month, October 2026) drops its X11 session**, and GNOME is doing the same. Building a brand-new identity on a shrinking platform is a bad trade. It stays the fallback if Sway misbehaves on this NVIDIA card.
5. **dwm, river, MangoWC, Qtile: not now** (reasons per section below).

---

## At a glance

| Candidate | NVIDIA (proprietary) | Maturity | Ease of setup | Tiling model | Terminal (TUI) ecosystem | Theming freedom | Community 2025–26 |
|---|---|---|---|---|---|---|---|
| **Sway** 1.12 (Wayland) | Works; explicit sync since 1.11; needs `--unsupported-gpu`; some app quirks reported | **High** — since 2016, 1.0 in 2019, ~1–2 releases a year, Arch `extra` | **Easy** — plain text, i3 format, good man pages | Manual (i3-style): you split, it fills; tabs and stacks; floating | **Best** — waybar, i3status-rust, fuzzel/rofi/fzf, mako, swaylock, swayidle, grim/slurp, i3-compatible IPC | Medium — border/title colours per state, gaps, fonts; no rounded corners/blur (SwayFX fork adds them) | "Rock-solid, basic but works"; the default recommendation for i3 users |
| **niri** 26.04 (Wayland) | Works; **no explicit sync yet**; known VRAM quirk with a workaround | Medium — since 2023, ~3 releases a year, Arch `extra`, one main developer | Easy — one KDL text file, good wiki, sensible defaults | **Scrolling**: windows in an endless row of columns per screen; floating since 25.01 | Very good — waybar, fuzzel, mako, swaylock; JSON IPC with event stream | High — borders, focus ring, gaps, shadows, rounded corners, **blur** (26.04) | Fastest-growing; ~24k GitHub stars; widely praised as stable |
| **Hyprland** 0.56.2 (Wayland) | Works well; explicit sync; popular with NVIDIA gamers; "not under our control" | Medium-low — since 2022, frequent big releases, **settings format changed to Lua in 0.55** | Medium — powerful but large, moving target | Dynamic (dwindle/master), user-defined layouts in Lua | Very good — its own hypr* tools plus waybar etc.; hyprctl IPC | **Highest** — animations, blur, shadows, rounded corners, motion blur | Loved for looks; known for churn and a controversial community |
| **i3** 4.25.1 (X11) | NVIDIA's oldest, most tested path; mixed refresh rates tear on X11 (ours are all 144 Hz, so fine) | **Highest** — since 2009, slow and careful, Arch `extra` | **Easiest** — plain text, the reference docs everyone copies | Manual, same as Sway | Very good, but X11 tools (i3bar, rofi, dunst, maim, xclip, picom) | Medium — same as Sway; effects need picom | Respected, but now the "legacy" choice |
| **dwm** 6.8 (X11) | Same as i3 | High age, tiny code; 6.6 → 6.8 in 2025–26; **AUR only** (chaotic-aur here) | **Hard** — settings are C code, you recompile; features come as patches | Dynamic master/stack | Small — its own bar, dmenu, scripts | High, but only by editing C | Admired, niche; for people who like patching C |
| **river** 0.4.8 (Wayland) | Not documented; wlroots-based like Sway | **Low right now** — 0.4 (March 2026) split the window manager into separate programs that are young | Medium-hard — you also pick a separate window manager | Whatever the chosen manager does (dwm-like, scrolling…) | Small but growing | Depends on the manager | Respected by tinkerers; in transition |
| **MangoWC** 0.17.x (Wayland) | Not documented (dwl/wlroots) | Low — rapid releases (three in one week, Sept 2026), AUR only | Medium | Many layouts, incl. scroller and master/stack | Has IPC | High — blur, shadows, rounded corners | Rising, small |
| **Qtile** 0.37 (X11; Wayland experimental) | X11 fine; Wayland backend rewritten, "experimental" | High on X11 | Medium — **settings are Python** | Several layouts | Built-in bar and widgets in Python | High | Liked by Python people |

---

## Candidates in detail

### 1. Sway — the i3 you already know, on Wayland

- **What it is:** a Wayland copy of i3: same keys, same settings language, same way of splitting windows. Written on *wlroots*, a shared building kit for Wayland compositors maintained by the same team.
- **Version and packaging:** 1.12 in Arch `extra` (`1:1.12-4` on this computer's package list). Sway 1.12 was released on 2026-05-25 with wlroots 0.20, bringing HDR (Vulkan renderer), capture of single windows and new protocols ([Phoronix via linux.org](https://www.linux.org/threads/phoronix-sway-1-12-released-with-hdr-support-on-vulkan-renderer-new-protocols.66838/), [wlroots 0.20 / Sway 1.12-rc1, Phoronix](https://www.phoronix.com/news/wlroots-0.20-Sway-1.12-rc1)).
- **NVIDIA:** Sway 1.11 (June 2025, wlroots 0.19) was the first with explicit sync (the `linux-drm-syncobj-v1` protocol), which NVIDIA's driver needs. You still start it with `sway --unsupported-gpu`, because the developers will not call a closed driver "supported" — they cannot debug it ([Michael Stapelberg, "Wayland/Sway in 2026"](https://michael.stapelberg.ch/posts/2026-01-04-wayland-sway-in-2026/)). Stapelberg (who created i3) ran Sway on an RTX 3060 Ti and RTX 4070 Ti in January 2026: it starts and works, but he hit a laggy mouse pointer, doubled key presses, Chrome's graphics process dying after resizes, and blurry old X11 apps when scaled. His case is extreme (an 8K screen over two cables), but the Chrome and pointer reports are worth testing for. One known game snag: some Vulkan games flicker with explicit sync on; `WLR_RENDER_NO_EXPLICIT_SYNC=1` turns it off as a workaround ([Wine bug 58423](https://list.winehq.org/hyperkitty/list/wine-bugs@list.winehq.org/thread/6PEGA7ZPZUPDWSWNGTUU2QIXMYKJA5K2/)). Older reports of flicker on NVIDIA with several screens above 120 Hz exist ([NixOS discourse](https://discourse.nixos.org/t/sway-nvidia-flickering/30994/12), [NVIDIA forum](https://forums.developer.nvidia.com/t/525-89-02-flickering-when-using-two-screens-at-120hz-on-4090-with-latest-driver/242488)) but most predate explicit sync. **Unproven for our exact setup until we try it.**
- **Our driver:** this desktop runs NVIDIA 615.71.09 with the open kernel modules — newer than every report above. NVIDIA added variable refresh rate (VRR) on multiple screens in 570 and more Wayland fixes in 580/590 ([9to5Linux via linux.org](https://www.linux.org/threads/9to5linux-nvidia-590-linux-graphics-driver-released-with-more-wayland-improvements.60278/latest), [linuxiac](https://linuxiac.com/nvidia-releases-linux-display-driver-v590-beta/)).
- **Gaming:** per-screen `adaptive_sync on` (VRR, the anti-stutter feature), `allow_tearing` for games that want the lowest delay, and `for_window [...] fullscreen enable` rules — the same kind of rule we needed for WoW on Hyprland. Wine's own Wayland driver keeps improving through Wine 11.x in 2026 ([Phoronix, Wine 11.11](https://phoronix.com/news/Wine-11.11-Released), [linuxiac, Wine 11.9](https://linuxiac.com/wine-11-9-improves-native-wayland-gaming-support/)) and works on any Wayland compositor.
- **Maturity:** started 2016, 1.0 in 2019, one or two releases a year, a team of maintainers rather than one person. The settings language is i3's and has stayed compatible for years — the opposite of Hyprland's churn.
- **Ease:** one plain text file (`~/.config/sway/config`), a complete example config ships with it, excellent `man sway` pages, and every i3 guide on the internet mostly applies. Truly barebones: a grey background, a simple bar, nothing else.
- **Tiling model:** manual — you choose whether the next window splits sideways or downwards; also tabbed and stacked groups, a scratchpad (a hidden pop-up window), and floating windows for dialogs and games.
- **Terminal-first ecosystem (all in Arch `extra`, checked):** bar `waybar` 0.15 or `i3status-rust` 0.36; launchers `fuzzel` 1.15, `rofi` 2.0 (now Wayland-native), or an `fzf` script in a floating terminal; notifications `mako` 1.11; lock `swaylock` 1.8.6; idle `swayidle` 1.9; screenshots `grim` + `slurp`; clipboard `wl-clipboard` + `cliphist`; wallpaper `swaybg` or `awww`. **Scripting:** `swaymsg` speaks the i3 IPC protocol (JSON over a socket, with event subscriptions), and the Python library `i3ipc` works with it — exactly what a future Forge app (Python/Textual) needs to read and steer the desktop.
- **Theming:** per-state colours for borders and title bars (focused, unfocused, urgent, each with border/background/text/indicator), gaps, border width, fonts, the bar's own colours. Enough for a clear brand identity with deliberate contrast between parts. **No rounded corners, shadows or blur** in plain Sway. **SwayFX** is a fork that adds them (blur, rounded corners, shadows, dimming of inactive windows) ([wlrfx/swayfx](https://github.com/wlrfx/swayfx)), version 0.6 on chaotic-aur here — but it is not in Arch's official repos and trails Sway's releases, so it is a later option, not the base.
- **Community:** the standard "minimal, rock-solid" recommendation; i3 users' natural move to Wayland.
- **Our screens' shared-name quirk:** Sway can address screens by connector (`DP-1`, `DP-2`…) instead of by make/model/serial, which sidesteps identical serials.

### 2. niri — scrolling tiling, the 2025–26 favourite

- **What it is:** a Wayland compositor written in Rust where each screen holds an endless horizontal row of columns; new windows open to the right and you scroll along, instead of squeezing everything into the screen.
- **Version and packaging:** 26.04 in Arch `extra` (`26.04-1`). Releases: 25.01, 25.02, 25.05, 25.08, 25.11 (Nov 2025), 26.04 (Apr 2026) ([niri releases](https://github.com/YaLTeR/niri/releases)). 26.04 added blur; 25.11 added an Alt+Tab switcher with live previews, real maximise and config includes; 25.08 integrated `xwayland-satellite` so old X11 apps "just work"; 25.05 added an overview of all workspaces.
- **NVIDIA:** works, and many people run it, but: (a) a known driver quirk makes niri use about 1 GiB of graphics memory instead of ~100 MiB until you add a small NVIDIA profile file (`GLVidHeapReuseRatio = 0`) ([niri wiki: Nvidia](https://github.com/YaLTeR/niri/wiki/Nvidia)); (b) screencast flicker in Discord/OBS on NVIDIA was fixed in 25.08; (c) **explicit sync is not in niri yet** — PR #3956 "add linux-drm-syncobj-v1 support" (opened 2026-05-02, updated 2026-09-15) and draft PR #3217 are still open, and issue #3562 reports high frame-present delays ([niri issue search](https://github.com/YaLTeR/niri/issues?q=explicit+sync)). For three 144 Hz screens and WoW on NVIDIA, that last point is the main risk.
- **Gaming:** VRR per screen (with an "on demand" mode); a debug option stops cursor movement from redrawing during VRR (25.08). X11 games go through `xwayland-satellite`; WoW with Wine's Wayland driver skips that.
- **Maturity:** public since 2023; releases roughly every three months and widely described as stable for daily use. The project moved to a GitHub organisation (`niri-wm`) in 26.04, but development is still mostly one person (Ivan Molodetskikh, "YaLTeR") — a single-maintainer risk.
- **Ease:** one KDL file (a simple bracket-and-quotes text format), a well-commented default config, a good wiki. The default config starts Waybar and uses Alacritty and fuzzel ([niri Getting Started](https://github.com/YaLTeR/niri/wiki/Getting-Started)).
- **Theming:** focus ring and border colours (also gradients), gaps, rounded corners, shadows, and now blur via window and layer rules. More visual room than Sway, less than Hyprland.
- **Scripting:** `niri msg --json` and an event stream; good for Forge apps.
- **Community:** ~24k GitHub stars, covered by LWN and big Linux YouTubers; Noctalia and DankMaterialShell both support it ([gittrend](https://gittrend.io/repo/niri-wm/niri), [It's FOSS](https://itsfoss.com/niri-window-manager.md)). Users describe it as more stable and focused than Hyprland. Note: some comparison sites in search results (e.g. factually.co) are low-quality summaries; they were not used as evidence.

### 3. Hyprland — what we are leaving

- 0.56.2 in Arch `extra`. 0.55 (2026) switched the settings to **Lua**, removed several options and a dispatcher; the old format works "for a few more releases" ([hypr.land 0.55 news](https://hypr.land/news/update55/), [Phoronix](https://phoronix.com/news/Hyprland-0.55-Wayland-Comp)). 0.56 (July 2026) had no breaking changes but needed 14 regression fixes a week later and 16 more in 0.56.2 ([linuxcompatible](https://www.linuxcompatible.org/story/hyprland-0562-released-16-backported-fixes-stabilize-the-056-series/)). 0.57 expected around October–November 2026.
- **NVIDIA:** explicit sync supported; the wiki says NVIDIA works but "some issues could arise … that we have no control over" ([Hyprland wiki: Nvidia](https://wiki.hypr.land/Nvidia/)). Gamers report it as a good NVIDIA/VRR/HDR choice.
- **Looks:** the richest — animations, blur, shadows, motion blur, rounded corners.
- **Community:** big and enthusiastic, but with a well-documented history of moderation controversy and a ban of its author from freedesktop.org ([hypr.land "On Hyprland Moderation"](https://hypr.land/news/onModeration), [desdelinux](https://blog.desdelinux.net/en/the-creator-of-hyprland-was-banned-from-freedesktop-and-is-now-banned-from-contributing-to-the-project/)).
- **Our own record:** the "every window maximised" bug (fixed upstream after 0.56.2), session crashes, and rewrites forced by format changes. It fails Javier's "mature and proven" test.

### 4. i3 — the most proven, on the old display system

- 4.25 (Dec 2025) and 4.25.1 (Feb 2026), in Arch `extra` ([Wikipedia](https://en.wikipedia.org/wiki/I3_(window_manager)), [Arch package](https://www.archlinux.org/packages/i3-wm)). Since 2009; slow, careful changes.
- **NVIDIA on X11** is the oldest, most tested path NVIDIA has. On X11 with several screens, one screen tears if refresh rates are not multiples of each other; **our three are all 144 Hz, so that does not bite**. Tearing is handled with NVIDIA's "force composition pipeline" or the `picom` compositor ([Arch forums](https://bbs.archlinux.org/viewtopic.php?id=280623)).
- **The X11 problem in 2026:** the official X.Org server only gets security fixes; feature work has stopped. A fork, **XLibre**, started in June 2025 and made its 25.1 series stable a year later (Artix uses it by default); it is controversial (its lead was banned from freedesktop.org), and NVIDIA support for it is not official ([linuxiac, XLibre 25.1](https://linuxiac.com/?p=213691), [NVIDIA forum: support for XLibre](https://forums.developer.nvidia.com/t/support-for-xlibre/336200)). **KDE Plasma 6.8 (October 2026) is Wayland-only** ([The Register](https://www.theregister.com/2025/11/28/kde_6_8_wayland_only/), [KDE's David Edmundson](https://planet.kde.org/david-edmundson-2026-06-02-ex-11-prepping-for-plasmas-last-x11-supported-release/)), and GNOME has deprecated its X11 session. On X11 there is no per-screen fractional scaling, and the newest Wine work targets Wayland.
- **Verdict:** the best *fallback* if Sway on this NVIDIA card fails our test; a poor place to build a new identity meant to last.

### 5. dwm — beautiful minimalism, built from C

- dwm 6.6 (2025-08-09), 6.7 (2026-01-10), 6.8 (2026-01-30, a regression fix) ([suckless.org](https://suckless.org/), [git.suckless.org](https://git.suckless.org/dwm)). **Not in Arch's official repos** (AUR; this computer sees it through chaotic-aur), so nog would need the AUR path — a finding under our "nog first" rule.
- Settings are **C source code**; every change means recompiling, and features (gaps, systray, colours per element) come as patches you merge by hand. X11, with all of i3's X11 caveats. Its Wayland cousin `dwl` is not in Arch's repos either.
- **Verdict:** the opposite of "easy to set up". Admired, but not for this restart.

### 6. river — promising, but mid-transition

- river 0.4 (2026-03-16) split itself in two: river now only draws and handles input, and **a separate window manager program** decides the layout, through a new stable protocol ([linuxiac](https://linuxiac.com/river-0-4-wayland-compositor-debuts-pluggable-window-managers/)). Window managers for it (kwm — dwm-like; Rill — scrolling; Canoe — stacking) are young. `river` 0.4.8 and the old-style `river-classic` 0.3.17 are both in Arch `extra`.
- No NVIDIA documentation found; it uses wlroots like Sway.
- **Verdict:** interesting for a future Forge-built window manager (we could write our own layout program), but not "mature and proven" today.

### 7. Others the community mentions

- **MangoWC** (dwl-based): many layouts, blur and rounded corners, IPC; very active but very fast-moving (0.17.0, 0.17.1, 0.17.2 in one week of September 2026) and AUR-only ([linuxcompatible](https://www.linuxcompatible.org/story/mango-wayland-compositor-0172-ships-stability-patch-for-dwlbased-compositor/)). Not mature yet.
- **Qtile:** settings and bar written in **Python**, which fits our Python/Textual skills; mature on X11, but its Wayland backend was rewritten and is officially "experimental" ([Qtile docs](https://docs.qtile.org/en/stable/manual/wayland_status.html)). 0.37.1 in Arch `extra`. Worth a look again in a year.
- **labwc:** a *stacking* (overlapping windows) compositor, not tiling; only relevant if Javier ever wants an Openbox-style floating desktop. Skipped.
- **Awesome:** X11, Lua; slow-moving. Skipped for the same X11 reasons as i3.

---

## Recommendation, ranked

### Top pick: Sway

Tied to Javier's priorities:
- **Mature and proven:** ten years old, team-maintained, one or two calm releases a year, settings format stable for years, so a config written today should still work in a year.
- **NVIDIA + 3 × 144 Hz:** explicit sync since 1.11; per-screen VRR and tearing control; this desktop's driver (615) is newer than any problem report found. The `--unsupported-gpu` flag is a label, not a limitation.
- **Easy:** one plain text file, i3's well-known language, a complete example config, the best documentation of any candidate.
- **TUI-friendly:** the largest set of small, keyboard-driven companion tools, all in Arch's official repos (so `nog` can install every one), and an i3-compatible JSON control socket that Python Forge apps can drive with an existing library.
- **Liked by the community:** the standard "it just works" recommendation.
- **Room for our own look:** colours for every border and title-bar state, gaps, fonts, and a bar we style ourselves. If we later want rounded corners or blur, SwayFX is a drop-in fork using the same config.

The honest trade-off: plain Sway has **no animations, no rounded corners, no blur**. Our identity has to come from colour, contrast, typography, the bar and the terminal — which fits "elements connected but not fused" well, but it will look plainer than Hyprland on day one.

### Runner-up: niri

Prettier than Sway and very well liked, in Arch's official repos, stable in practice. Second because it is young with one main developer, and **its explicit sync support has not landed** — the very thing NVIDIA needs, on a desktop with three 144 Hz screens and a game. Its scrolling layout is also a new way of working that Javier would need to try before committing.

### What would change this recommendation

- **Sway misbehaves on this card in a test session** (flicker on the 144 Hz screens, Chrome losing graphics acceleration, a laggy pointer, WoW stutter that `WLR_RENDER_NO_EXPLICIT_SYNC=1` does not fix) → try niri next; if both fail on NVIDIA, i3 on X11 as the proven fallback.
- **niri merges explicit sync** (PR #3956) and Javier likes the scrolling layout in a trial → niri moves to first place.
- **Javier decides animations and blur are part of the identity** → SwayFX (same config as Sway, but outside the official repos), or niri.
- **A Python-configured desktop becomes attractive** (Forge apps and the window manager in one language) → revisit Qtile once its Wayland backend leaves "experimental".

### Suggested next step (for Javier to approve, nothing done yet)

Install Sway from Arch `extra` with `nog`, add it as an extra login choice in SDDM next to Plasma and the current hypeForge session, and run a short written test: three screens at 144 Hz, Chrome with a video, Discord screen share, WoW full screen, brightness with ddcutil. The result decides between Sway and niri before any styling work starts.

---

## Commands run on this computer (all read-only)

```
pacman -Si sway niri hyprland i3-wm dwm river river-classic swayfx qtile labwc \
  waybar fuzzel rofi mako swaylock swayidle hyprlock grim slurp wl-clipboard \
  cliphist swaybg awww i3status-rust xwayland-satellite     # repo + version
pacman -Si mango tofi yambar dwl swww                      # not found in any repo
pacman -Q nvidia-open-dkms                                  # 615.71.09-1
nvidia-smi --query-gpu=name,driver_version --format=csv     # RTX 3060, 615.71.09
```

## What I could not verify

- **No hands-on test on this desktop** — every NVIDIA statement here is from other people's reports, not from our RTX 3060 and three screens.
- **niri's explicit sync**: I confirmed the pull requests are open; I could not confirm how much its absence actually hurts on driver 615.
- **The Arch wiki** pages for Sway and NVIDIA blocked automated reading (an anti-bot page), so Arch wiki guidance is not quoted directly.
- **river and MangoWC on NVIDIA**: no documentation or reports found either way.
- **Reddit (r/unixporn, r/archlinux)** threads were not reachable through search in a usable form; community sentiment comes from LWN, Phoronix, linuxiac, It's FOSS, forums and the projects' own pages.
