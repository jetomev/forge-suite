# defaultappsForge — section rules

*A Forge Suite app (D-60): which app opens what. Read the suite's `CLAUDE.md` first; this file adds what is particular here.*

- **One job: default apps** — the kinds (browser, files, text, PDF, pictures, music, video, documents, archives…) and, for the one-off, single file types. Nothing else.
- **The standard file only:** `~/.config/mimeapps.list` (freedesktop.org), read by every desktop and app; a backup before every save; the file must read back the same. Unknown sections and lines are kept.
- **Truth from the machine:** the apps and what each can open come from the desktop entries (`MimeType=`); "the system's guess" is what `xdg-mime` / the standard lookup answers. Never invent an association.
- **A design is approved by Javier, screen by screen, before code is written** (`docs/design/`, checked at 100 columns).
- **Built on forgekit, the Forge look;** keys from the menu, buttons "Words (key)", pop-ups for Change and Save, quitting with unsaved changes asks; `--hypeforge`.
- **Where it runs, said everywhere:** any Linux distribution · any desktop or none · any terminal, a plain text console too.
- Packages through nog; decisions in `docs/DECISIONS.md`; TODO.md after every step; plain words. Versioning: tags `defaultappsforge-vX.Y.Z`, AUR `defaultappsforge` after Javier's local test.
