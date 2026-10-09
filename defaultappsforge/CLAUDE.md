# defaultappsForge — section rules

*A Forge Suite app (D-60): which app opens what. Read the suite's `CLAUDE.md` first; this file adds what is particular here.*

- **One job: default apps** — Javier's fourteen (Web Browser, Email Client, Calendar, Phone Numbers, Image Viewer, Music Player, Video Player, Text Editor, PDF Viewer, File Manager, Terminal Emulator, Archive Manager, Map, Office Suite), each a drop-down, and the common file types assigned to them (D-2…D-4). Nothing else.
- **The standard file only:** `~/.config/mimeapps.list` (freedesktop.org), read by every desktop and app; a backup before every save; the file must read back the same. Unknown sections and lines are kept.
- **Truth from the machine:** the apps and what each can open come from the desktop entries (`MimeType=`); "the system's guess" is what `xdg-mime` / the standard lookup answers. Never invent an association.
- **A design is approved by Javier, screen by screen, before code is written** (`docs/design/`, checked at 100 columns).
- **Built on forgekit, the Forge look;** keys from the menu, buttons "Words (key)", drop-downs for the choice, a pop-up for Save, quitting with unsaved changes asks; `--hypeforge`.
- **Where it runs, said everywhere:** any Linux distribution · any desktop or none · any terminal, a plain text console too.
- Packages through nog; decisions in `docs/DECISIONS.md`; TODO.md after every step; plain words. Versioning: tags `defaultappsforge-vX.Y.Z`, AUR `defaultappsforge` after Javier's local test.
