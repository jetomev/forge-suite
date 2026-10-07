# sudoForge — research (2026-10-06)

*What has to be true for one password box to answer every admin request in a Sway session, and what was proven on the test desktop (`tphome-linux`, Arch, Sway 1.12, polkit 127, sudo 1.9.17p2) before any code was written.*

## The job (hypeForge D-56, D-61)

On a Sway desktop nothing answers two kinds of password question:

1. **The admin pop-up (polkit).** A program asks the system for admin rights, for example to mount a USB stick or add a printer. The system then looks for the session's *authentication agent* to ask the person. On Plasma that is KDE's pop-up. On Sway there is none, so the request fails without a word (hypeForge F-44, forge-suite#26).
2. **The sudo password window (askpass).** `sudo -A` runs a helper program to ask for the password instead of the terminal. Sway sets none, so `sudo -A` (and nog with `NOG_ASKPASS=1`, and Claude's own admin commands) cannot ask at all (hypeForge F-42, forge-suite#24).

sudoForge answers both with forgekit's password box in a small floating window, the same look as every Forge app.

## Measured on this computer

| Fact | How it was checked | Result |
|---|---|---|
| No polkit agent runs for the Sway session | `busctl --user list`, process list | none (only the Snap session agent) |
| `SUDO_ASKPASS` is unset in the session | the session environment | unset |
| A box can be on screen fast enough | timed `alacritty -e true` and `import forgekit, textual` | 0.14 s + 0.20 s ≈ 0.35 s, so the window can be opened only when needed |
| The floating window lands right | Claude Desktop's Quick Entry, a small window, on this Sway | floats centred with no rule; sudoForge still gets its own rule to be sure |

## Proven before writing code

### 1 · The sudo helper can tell which command is asking (design screen 3)

sudo hands its helper only the words `[sudo] password for jetomev:`. The helper's **parent process is sudo itself**, and its full command line can be read from `/proc/<parent>/cmdline`.

Test: a throwaway helper that records what it sees and **gives no password** (so sudo refuses and nothing runs):

```
SUDO_ASKPASS=probe.sh sudo -A -k pacman -S --needed firefox
→ sudo: no password was provided   (exit 1)
prompt: [sudo] password for jetomev:
parent cmdline: sudo -A -k pacman -S --needed firefox
parent comm: sudo
```

So the box can show the command in orange under its title. The sudo flags (`-A -k`) are dropped from what is shown; only the command that will run as admin is shown.

### 2 · One agent can answer for the whole session (design screens 1, 2, 4)

forgekit's `InAppPolkitAgent` (0.6.0) signs up **for its own process only** (`Polkit.UnixProcess`). sudoForge must sign up **for the login session** (`Polkit.UnixSession`, `XDG_SESSION_ID`).

Test: a throwaway agent registered for session 2, answering every request with *Cancel*; then a **separate** program with no terminal asked for admin rights:

```
registered for session 2
pkexec exit: 126 Error executing command as another user: Request dismissed
requests seen: [{'action': 'org.freedesktop.policykit.exec',
  'message': "Authentication is needed to run `/usr/bin/true' as the super user",
  'details': {'polkit.caller-pid': '325162', 'polkit.subject-pid': '325155'}}]
unregistered
```

The request reached our agent with what the box needs: the **kind of request** (`action`, for the plain-words title), **the system's own sentence** (`message`) and **which program asked** (`polkit.subject-pid` → `/proc/<pid>/comm`, for "Asked by …"). Cancel was honoured and nothing ran.

### 3 · Where sudo learns about sudoForge (D-3)

Two ways were looked at:

- **`/etc/sudo.conf`: `Path askpass /usr/lib/sudoforge/sudoforge-askpass`** — sudo reads it whatever the shell, the login screen or the program. `SUDO_ASKPASS`, when set, still wins, so Plasma keeps its own window. The file belongs to the `sudo` package and is one of its **backup files** (`pacman -Qii sudo`), so an update never overwrites the line; a new default arrives as `sudo.conf.pacnew` beside it. Today the file has **no active lines**.
- A login setting in the home folder. Under today's login screen (SDDM) whatever fish exports at login reaches Sway (SDDM's `wayland-session` script runs the user's login shell), but it depends on the login screen, and KognogOS will have its own (greetForge).

Javier chose `/etc/sudo.conf`. Because it is outside `$HOME`, **sudoForge applies it itself, with a backup and an undo** (hypeForge rule: nothing outside `$HOME` edited by hand).

### 4 · nog (D-4)

nog uses `sudo -A` only when `NOG_ASKPASS=1` (`src/machine.rs`, `askpass()`); otherwise it asks in the terminal. Javier chose to keep that: **in a terminal, nog and plain `sudo` ask in the terminal**; the box appears for `sudo -A`, for nog started without a terminal or with `NOG_ASKPASS=1`, and for every polkit request.

## The shape that follows

```
login ─► sudoforge (background, no window)
          ├─ polkit agent for the session ─┐
          └─ private socket (0700 folder,  │  a request
             one-time token) ◄─ sudoforge-askpass ◄─ sudo -A
                                           ▼
                 alacritty --class sudoforge -e <the box>   (floating, centred, focused)
                                           │ password
            polkit: PolkitAgent.Session checks it  /  sudo: printed to sudo only
```

- **One box at a time.** A second request waits for the first to be answered.
- **The password is never written anywhere**: not to disk, not on a command line, not in a log. For polkit, polkit's own setuid helper checks it (sudoForge never gets root and never decides if it is right); for sudo, it goes back over the socket and is printed once, to sudo.
- **Three tries** for polkit, the way polkit's own agents do it; sudo counts its own tries.
- **Who's asking, in plain words.** A short table turns the request kind into a name (`org.freedesktop.udisks2.*` → "USB drives", `org.opensuse.cupspkhelper.*` → "Printers", `org.freedesktop.policykit.exec` → the program's name …); anything not in the table shows the program's name.
- **No Sway, no box.** On a text console the helper says so and sudo falls back to asking in the terminal (plain `sudo`), as today.
- **Started at login** by hypeForge's Sway config, like the other applets; a Sway rule floats and centres `app_id=sudoforge`.

## forgekit: the centred password field (D-2)

Javier wants the typed password's dots centred. Textual 8.2.8's `Input` has no text alignment (`text_align` / `text-align` appear nowhere in `textual/widgets/_input.py`). forgekit gets its **own password field**: it takes each key, keeps the password in memory only, and draws one dot per character, centred. Every Forge app's password box gets it, not only sudoForge.

## Still to prove while building

- The box takes the keyboard the moment it opens on every screen (Sway's focus on a new window), including over a full-screen app.
- Two requests at the same moment (queueing).
- polkit's tries counted right when the box is cancelled half way.
- The text-console fallback, in the KognogOS VM.
- The Claude Desktop keyring is **not** part of this (D-61); it gets its own research afterwards.
