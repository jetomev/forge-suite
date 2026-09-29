# hypeForge — decision log

*Every decision that shapes hypeForge, dated, with who made it and why. Newest first.*
*A decision here is only reopened by Javier. **Proposed** entries are suggestions still waiting for his answer.*

---

## 2026-09-28 — the first night

### D-13 · Documentation is written at every step, starting tonight
**Decided by Javier.** The project gets its full GitHub presence from the first night. That means the README, About, topics, labels, milestones and issues. Documentation is written as the work happens, not afterwards. The public project page at [kognogos.org](https://kognogos.org) announces hypeForge as coming soon.

### D-12 · How testing is done: virtual machines, then this desktop
**Decided by Javier:** testing happens in virtual machines. The existing test machine (`kognog-test`) **is not a real KognogOS install**. It was put together by hand without the KognogOS apps and settings. **The KognogOS installer image has to be fully rebuilt** so that a virtual machine can get a proper KognogOS install. That rebuild is KognogOS work, and hypeForge's KognogOS testing waits on it.
**Decided by Javier, the same night:** also build an **Omarchy virtual machine** as the hands-on reference. See D-4.

### D-11 · The recipe: up to five researched options per job, and Javier chooses
**Decided by Javier.** For every job (top bar, launcher, notifications, file manager…), the recipe shows **no more than five options**. They are the most reviewed and most recommended ones, each with links to sources that show how it works. Javier makes every choice. Claude may add a one-line suggestion, clearly marked as a suggestion. → [RECIPE.md](RECIPE.md)

### D-10 · Forge apps run in Alacritty, and must be readable on a plain text screen
**Decided by Javier.** Under hypeForge, the Forge apps (hypeForge included) run in Alacritty, exactly as they do today. He also agreed with the fix for [forgekit#1](https://github.com/jetomev/forgekit/issues/1): the Forge apps are currently hard to read on a plain text screen. hypeForge will often be started from a text screen, because a fresh Arch install has no desktop yet. So that fix has to land **before hypeForge ships**.

### D-9 · Updates are locked by us, through nog
**Decided by Javier:** *"nog treatment will be locked by us, to ensure it updates when needed."*
**Why:** Hyprland is linked to exact versions of six small helper packages (aquamarine, hyprcursor, hyprgraphics, hyprlang, hyprutils, hyprwire). All seven have to update together or the desktop breaks. Out of the box, nog treats all of them as ordinary packages (Tier 3, a 7-day wait) and has no way of knowing they belong together.
**What it means:** hypeForge owns a nog **group** for the Hyprland family, so the whole family moves together, and the family gets a tier we choose. The details are designed in Phase 3. → [DESIGN.md](DESIGN.md#updates-locked-by-us)

### D-8 · One portable folder; system changes only through the app
**Decided by Javier:** *"Everything from the beginning has to be installed through apps, libraries, and config files, properly saved in a folder for Hyprland to access, and easily portable. Whatever has to be installed in system folders has to be through an app using our config files."*
**Why:** installing, backing up and moving to a new computer all become simple. The folder is the backup.
**What it means:** nothing outside the home folder is ever edited by hand. The hypeForge app applies those pieces from files kept in the folder. → [DESIGN.md](DESIGN.md#one-portable-folder)

### D-7 · Floating windows by default; Win + arrow keys tile, like Plasma
**Decided by Javier:** *"Our window system has to be built to support floating windows by default, always, and tiling will come using Win+arrows to tile, simple, same as Plasma."*
**Note:** Hyprland is built for tiling first. Making every window float and adding Plasma-style snapping is possible, but it works against Hyprland's grain, so it gets proven early (Phase 1) before anything else is built on it. The key map copies the shortcuts Plasma uses on the test desktop today (read from its settings on 2026-09-28). → [DESIGN.md](DESIGN.md#floating-first-windows)

### D-6 · Plasma will be replaced
**Decided by Javier:** *"We will ditch Plasma and keep a lighter UI system. This will reshape some of our KognogOS decisions little by little, but it is a thing."*
**What it means:** hypeForge becomes the KognogOS desktop, and KognogOS moves off Plasma step by step. → [KOGNOGOS-IMPACT.md](KOGNOGOS-IMPACT.md)
**Decided by Javier, the same night:** *"Only when hypeForge works and I am fully daily driving it is when we will take down Plasma."* Until then, Plasma stays installed on the test desktop as a **fallback login choice**, so there is always a working desktop to log into while the new one is built. The condition is **daily driving**, which is more than passing tests.

### D-5 · Hyprland settings are written in Lua, from day one
**Decided with Javier (following Hyprland upstream).** From version 0.55, Hyprland's settings are written in **Lua**. The old format is supported for *"1 – 2 releases starting from 0.55. After that, hyprlang will be dropped"* ([Hyprland, 26 April 2026](https://hypr.land/news/26_lua/)). Version 0.56 is already current, so we write Lua only. Omarchy 4 made the same move.

### D-4 · Omarchy is the reference
**Decided by Javier:** [Omarchy](https://github.com/basecamp/omarchy) (MIT) is *"our reference, definitive."*
**Worth knowing:** Omarchy 4 "Quattro" (14 August 2026) replaced its separate small apps (Waybar, Walker, Mako, SwayOSD, hyprlock, hypridle, swaybg, polkit-gnome) with **one Quickshell-based desktop program**. So "follow Omarchy" and "light, separate apps" now point in different directions. The recipe asks that question first.
**Decided by Javier, the same night:** build an Omarchy virtual machine. Hyprland needs 3D graphics, even inside a virtual machine, and the virtual machines on this NVIDIA desktop have never had 3D switched on. Omarchy is a known-good Hyprland setup, so if the machine works, we know the test setup works before we test our own work in it.

### D-3 · The desktop is built on Hyprland
**Decided by Javier.** Hyprland 0.56.2 is in Arch's official repositories. It supports floating and tiled windows, and it is the base Omarchy uses.

### D-2 · It is a full project, run with the usual method
**Decided by Javier.** The project gets a full public GitHub presence, phased releases, a published test matrix with numbered findings, issues opened and closed with full explanations, and co-author credit on every commit.

### D-1 · The name is hypeForge
**Decided by Javier.** It follows the Forge Suite naming rule: `[name]Forge`, lowercase first letter. The repository and package name is `hypeforge`.
**Checked on 2026-09-28:** the name is free on the AUR and at `jetomev/hypeforge`. No other GitHub project called hypeforge is a Linux desktop tool.
**Flagged to Javier the same night:** `hypeforge` is one letter away from `hyprforge`, an active GitHub project that builds Hyprland desktop apps ([hyprforge-suite](https://github.com/hyprforge-suite/hyprforge)). The name `hyprForge` was avoided for that reason. Keeping the one-letter neighbour is Javier's call.
