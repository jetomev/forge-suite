# Default apps

**What it does:** decides which app opens what: web links, email, calendar invites, pictures,
music, video, text, PDFs, folders, archives, maps, documents, and your terminal.

## defaultappsForge

Settings → **Default apps**, or the launcher (Settings → defaultappsForge).

- **Default Apps:** fourteen jobs, each with a drop-down of the apps that can do it: Web
  Browser · Email Client · Calendar · Phone Numbers · Image Viewer · Music Player · Video Player ·
  Text Editor · PDF Viewer · File Manager · Terminal Emulator · Archive Manager · Map · Office Suite.
- **File Types:** the common file types and which default app opens each. Tick types on the left,
  open a default app on the right, **>>** assigns them, **<<** clears them (like workspaceForge).
- **F10** saves, with a review first; a backup of the old file; at once.

It writes the standard list every desktop reads (`~/.config/mimeapps.list`), so a choice holds in
Plasma and in every app too. The terminal goes to `~/.config/xdg-terminals.list`; once you've
chosen one there, **Win + Enter** opens it.

## From a terminal

`handlr` still works for a one-off: `handlr open report.pdf` opens it with its default app;
`handlr get .pdf` says which one.
