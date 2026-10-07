# Default apps (handlr)

**What it does:** decides which app opens which kind of thing: web links, text files, pictures,
music, video, PDFs, folders. Sway has no settings page for this, so for now hypeForge uses
**handlr** in a terminal (Alacritty). It writes the standard list every desktop reads
(`~/.config/mimeapps.list`), so a choice made here also holds in Plasma and in every app.

## The three commands

| Do | Command |
|---|---|
| See every choice | `handlr list` |
| See one | `handlr get text/plain` · `handlr get x-scheme-handler/https` · `handlr get .pdf` |
| Set one | `handlr set .pdf masterpdfeditor4.desktop` · `handlr set x-scheme-handler/https google-chrome.desktop` |

The app's name is its launcher file: `ls /usr/share/applications ~/.local/share/applications`
lists them (for example `google-chrome.desktop`, `fresh.desktop`, `thunar.desktop`).
A kind can be a file ending (`.pdf`, `.png`) or a type (`text/plain`, `image/png`,
`inode/directory` for folders, `x-scheme-handler/https` for web links).

## Open something with its default app

`handlr open ~/Documents/report.pdf` or `handlr open https://kognogos.org`: the same as
clicking it. `handlr unset .pdf` takes a choice back.

## Coming

A **Default apps** Forge app in the hypeForge Settings (a list of kinds and the app for each,
no commands to remember) replaces this page. Until then, KDE's own page also works while Plasma
is still installed: `kcmshell6 kcm_componentchooser`.
