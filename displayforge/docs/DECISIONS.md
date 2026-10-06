# displayForge — decision log

*Newest first. Who decided, when, and why.*

## 2026-10-06

### D-4 · displayForge 1.0.0 is done
**Decided by Javier** (2026-10-06): *"great tool my friend! looks and works wonders. I still have to test a little more the arrange section, but so far good. Let's say v1.0 is done! make it official, full documentation."*
**What that rests on:** Javier's own run on the three Sceptres (Screens, Settings with try-and-keep, Identify, Brightness, names), which found F-1, F-2 and F-3, all fixed; 48 automatic tests. **Not yet tested, said in the release notes:** one- and two-screen setups (a VM), the 80 / 90 % sizes on real apps, a plain text console, and the rest of Arrange on the real screens. Findings from those become 1.0.x fixes.
**Version:** the planned 0.1.0 became 1.0.0 — the scope of the approved design is complete. Tag `displayforge-v1.0.0` (Forge Suite: every app keeps its own version and tags).

### D-3 · Identify without the big numbers on the screens
**Decided by Claude, told to Javier** (2026-10-06): the design showed a big number drawn on each screen during Identify. Left out: it needs a window placed on every monitor, and the Screens drawing already shows which number is which. Identify instead **dims one screen at a time** and asks which went dark — the screens tell themselves apart. Javier ran it and kept it.

## 2026-10-05

### D-2 · The design is approved, with Javier's changes
**Decided by Javier** (on the design page, 2026-10-05): *"Wow!!!! I love what you have done! Let's go!"* — the seven questions taken as answered by the recommendations, plus:
- **Any arrangement**: *"Could we arrange up to 4 monitors, one next to the other? … 3 on top and 3 bottom? … I used to have 4 monitors, and the 4th was under 1."* Sway places screens anywhere, so Arrange works for any layout — rows, grids, a screen under another.
- **Size below 100 %**: 80 % and 90 % added (with the note that older X11 apps look slightly blurry at non-whole sizes — Sway's own manual). Proven in the test VM before it is offered.
- **Brightness in tens**: 10 % … 100 %, on each screen and for all screens.
- **HDR**: shown only for screens that support it — Sway reports it per screen; Javier's Sceptre Y27s report no HDR, so for them it reads "not supported by this screen".
- **Names**: screens can be named (Identify), and the names are shown everywhere in displayForge.
- Scope 0.1.0: Screens, Settings, Arrange, Brightness, Identify; try first (F9, countdown), then save (F10); "main screen" = where the workspaces start (screen 1); brightness not saved (the screens keep it); only real options offered; saved to `~/.config/sway/outputs` with a backup; night light a later version.

### D-1 · displayForge: our own screen-settings app, in the terminal
**Decided by Javier:** "Monitor Settings please" → of the options (our own Forge app, the graphical nwg-displays as a stopgap, both) → **build the Monitors Forge app**; name **displayForge**.
**Why:** no terminal app arranges screens on Sway (hypeForge D-57: terminal first); every setting is its own Forge app (hypeForge D-59). Research: `docs/research/2026-10-05-displayforge.md`.
