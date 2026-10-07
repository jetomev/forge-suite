# Passwords (sudoForge)

**What it does:** whenever something needs admin rights, **one small box** opens in the
middle of the screen you are using: an app mounting a drive or adding a printer, a
`sudo -A` command, or nog started from the launcher. It says **who is asking and what for**,
then asks for your password.

## How to use it

- Type your password: only dots show, in the middle of the field.
- **Enter** = OK, **Esc** = Cancel. Cancel means nothing runs.
- A wrong password says so in yellow and shows **try 2 of 3** at the top.
- One box at a time: a second request waits until the first is answered.

In a terminal, `sudo` and nog still ask right there in the terminal. The box is for
everything that has no terminal to ask in.

## Safe by design

- Your password goes **only** to the system (polkit) or to sudo, which check it. sudoForge
  never keeps it, never writes it anywhere, and never gets admin rights itself.
- Its record (`~/.local/state/sudoforge/service.log`) says what asked and how it ended, never the password.

## Settings

- `sudoforge status` — is it running, and is `sudo -A` set up?
- `sudoforge setup` — makes `sudo -A` use the box (one line in `/etc/sudo.conf`, with a backup;
  it asks for your password once, in the box itself).
- `sudoforge undo` — takes that line back out.

It starts by itself when you log in to Sway.
