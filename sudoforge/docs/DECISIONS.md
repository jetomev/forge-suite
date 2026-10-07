# sudoForge — decision log

*Newest first. Who decided, when, and why.*

## 2026-10-06

### D-4 · nog and sudo in a terminal keep asking in the terminal
**Decided by Javier**, from the options: *"In the terminal"*. The sudoForge box appears for `sudo -A`, for nog started without a terminal (or with `NOG_ASKPASS=1`) and for every admin pop-up (polkit). Typing in a terminal stays in that terminal.

### D-3 · sudo learns about sudoForge from its own settings file
**Decided by Javier**, from the options: `/etc/sudo.conf` gets `Path askpass …`, so it works in every shell, from any login screen (today's SDDM and the future greetForge), for scripts and for Claude. It is a system file: **sudoForge applies it itself, with a backup and an undo**. It is one of the sudo package's backup files, so updates do not overwrite it.

### D-2 · The box's design is approved; the password's dots are centred
**Decided by Javier** after three rounds on the design page (https://claude.ai/artifact/J1CtQopNBRmQmJUTohwq9u, private): floating, centred on the screen in use. The title (*"USB drives wants admin rights"*) in its own bar, the password box's width, 2 points bigger, bold white on the KognogOS Mocha window colour `#1e1e2e`, wrapping if long; the two lines under it centred; a blank line before *"Password for jetomev"*, centred; the dots centred as they are typed. The sudo box: the same title bar (*"nog wants to run as admin"*), the command in orange under it, no box around it. Wrong password: a yellow line, *"try 2 of 3"* in the top bar. Enter = OK, Esc = Cancel.
The centred dots need a password field of our own (Textual's cannot centre): **built into forgekit**, so every Forge app gets it (Javier: *"build it into forgekit"*).

### D-1 · The name and the job
**Decided by Javier** (hypeForge D-56 and D-61): **sudoForge**, our own password helper for the Sway session, answering the admin pop-up (polkit) and the sudo password window (askpass) with forgekit's password box. KDE's helpers are out (KognogOS ships with Sway only). The keyring (saved logins) is not part of version 1.
