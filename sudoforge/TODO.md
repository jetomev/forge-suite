# sudoForge — the list

**Started 2026-10-06.** A Forge Suite app (terminal, forgekit) that answers every password question in a Sway session: the admin pop-up (polkit) and `sudo -A` / nog, in one floating box. Section of the Forge Suite (D-60). Closes hypeForge F-44 (#26) and F-42 (#24). Updated after every step.

## Phase 0 · Research and design
- [x] Name: **sudoForge** (Javier, 2026-10-06; D-1)
- [x] Design approved (D-2): https://claude.ai/artifact/J1CtQopNBRmQmJUTohwq9u — four screens (on the desktop, admin pop-up, sudo/nog, wrong password), three rounds of Javier's notes
- [x] Research: `docs/research/2026-10-06-sudoforge.md` — **proven**: the sudo helper can read which command asks (its parent is sudo); one agent signed up for the session receives other programs' requests (kind, sentence, who asked); `/etc/sudo.conf` is a backup file of the sudo package
- [x] Where sudo learns about it: `/etc/sudo.conf`, applied by sudoForge with a backup and an undo (D-3)
- [x] nog / sudo in a terminal keep asking in the terminal (D-4)

## Phase 1 · Build
- [ ] The section's kit: `CLAUDE.md`, `README.md`, `docs/ROADMAP.md`, `docs/CHANGELOG.md`, tests folder (same shape as displayForge)
- [ ] **forgekit: the centred password field** (D-2) — our own field, dots centred, the password in memory only; every Forge app's password box uses it (forgekit release first)
- [ ] The background service: polkit agent for the session + the private socket; one box at a time
- [ ] `sudoforge-askpass`: asks the service, shows the command (from sudo's parent process), prints the password to sudo only; no Sway → says so and fails cleanly
- [ ] The box: forgekit app in `alacritty --class sudoforge`, the approved layout; plain-words names table for request kinds
- [ ] Apply / undo for `/etc/sudo.conf` (backup first), through the admin pop-up itself
- [ ] hypeForge: start at login + a Sway rule (float, centre) + a Help page
- [ ] Tests, in the failing direction too (wrong password, cancel, two requests at once, no Sway)

## Phase 2 · Javier's run, then release
- [ ] Test matrix in `testing/`; Javier's run (USB stick, printer, `sudo -A`, nog from the launcher, wrong password ×3)
- [ ] Release 1.0.0: tag `sudoforge-v1.0.0`, GitHub Release, AUR; close #26 and #24

## Later
- [ ] The keyring (saved logins for Claude Desktop, Chrome, Discord) — its own research (hypeForge D-61)
