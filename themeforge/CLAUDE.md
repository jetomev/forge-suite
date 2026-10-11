# themeForge — section rules

*A Forge Suite app (D-60): the look of the desktop. Read the suite's `CLAUDE.md` first; this file adds what is particular here.*

- **One job: hypeForge's look.** Many layers, page by page (Javier, 2026-10-11): first the **Theme Picker** (the theme = hypeForge's style, and its colours); later the pop-ups, icons, fonts, corners and the rest, each its own page. Nothing outside the look.
- **hypeForge does the switching.** themeForge reads hypeForge's files (the styles, the colour themes, what is applied: `~/.config/hypeforge/theme/state.toml`) and runs hypeForge's own command, `hypeforge-theme apply | undo`. It never writes a look file itself and never imports hypeForge's code (hypeForge D-59).
- **Truth from the machine:** the styles, themes and names come from hypeForge's files; nothing is copied into themeForge. A new style or theme shows up without a themeForge change.
- **Built on forgekit, the Forge look;** keys from the menu, buttons "Words (key)", drop-downs for the choice, Apply in the changes bar at the bottom, Undo on the page; `--hypeforge` (its Settings page is **Look**).
- **Where it runs, said everywhere:** any Linux distribution · **hypeForge on Sway** (it switches hypeForge's look) · any terminal, a plain text console too.
- **Tests on throwaway folders and a stand-in look;** a real apply is tried on the desktop only through the same `Look` code, and put back.
- Packages through nog; decisions in `docs/DECISIONS.md`; TODO.md after every step; plain words. Versioning: tags `themeforge-vX.Y.Z`, AUR `themeforge` after Javier's local test — the AUR waits until the full themeForge is done (Javier, 2026-10-11).
