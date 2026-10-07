# sudoForge — the list

**Started 2026-10-06.** A Forge Suite app (terminal, forgekit) that answers every password question in a Sway session: the admin pop-up (polkit) and `sudo -A` / nog, in one floating box. Section of the Forge Suite (D-60). Closes hypeForge F-44 (#26) and F-42 (#24). Updated after every step.

## Phase 0 · Research and design
- [x] Name: **sudoForge** (Javier, 2026-10-06; D-1)
- [x] Design approved (D-2): https://claude.ai/artifact/J1CtQopNBRmQmJUTohwq9u — four screens (on the desktop, admin pop-up, sudo/nog, wrong password), three rounds of Javier's notes
- [x] Research: `docs/research/2026-10-06-sudoforge.md` — **proven**: the sudo helper can read which command asks (its parent is sudo); one agent signed up for the session receives other programs' requests (kind, sentence, who asked); `/etc/sudo.conf` is a backup file of the sudo package
- [x] Where sudo learns about it: `/etc/sudo.conf`, applied by sudoForge with a backup and an undo (D-3)
- [x] nog / sudo in a terminal keep asking in the terminal (D-4)

## Phase 1 · Build
- [ ] The section's kit: `CLAUDE.md` ✅ (2026-10-06), tests folder ✅; `README.md`, `docs/ROADMAP.md`, `docs/CHANGELOG.md` with the release
- [x] **forgekit: the centred password field** (D-2) — **forgekit 0.8.0 released 2026-10-06** (#34): `PasswordField` + the layout pieces in `PasswordDialog`, 104 forgekit tests, five apps pass on it; Javier: "perfect! great job!"
- [x] The background service (`service.py`, `agent.py`, 2026-10-06): polkit agent for the **session** (adapted from forgekit's in-app one — fold back into forgekit later), the sudo door (private 0700 folder, SO_PEERCRED, the asker's parent must be sudo), one box at a time, a cancel closes the box; its record in `logs/service.log` (never the password). `main.py service`; `scripts/start-service`
- [x] `sudoforge-askpass` (stdlib only): asks the service, the service reads the command from sudo itself, the password printed to sudo only; no service → plain words + exit 1
- [x] The box (`box.py`): forgekit's `PasswordDialog` in sudoForge's layout, in `alacritty --class sudoforge` (66×24), one-time socket + token in its environment; `words.py` = the plain-words lines (request kinds → names, who asked past shells/sudo, the terminal, polkit's sentence → "To …"). **First live test (21:25) found F-1**: the box crashed on start — forgekit's colours (`$forge-*`) are only loaded by `ForgeApp`, and the stand-in box in the tests could not see it; nothing ran (sudo: no password). Fixed (`get_css_variables`), plus `tests/test_box.py`: the REAL box headless (5 tests, all 5 fail with the bug put back). Seen live after the fix: floating, focused, centred on the screen in use (DP-2), the approved layout. **Live test 2 (21:27) PASS: Javier typed his password in the box, `sudo -A -k true` exit 0** (log: "sudo asks (try 1): true" / "sudo: answered", no password). Forge apps run as `python main.py` are named by their folder ("sudoForge", not "main")
- [x] Apply / undo for `/etc/sudo.conf` (`sudoconf.py`; backup first, only our two marked lines, refuses if another helper is set, atomic write keeping permissions), run as admin through `pkexec` → asked in sudoForge's own box. `sudoforge setup` / `undo` / `status`. **Not run on the real file yet**
- [x] hypeForge: start at login (`exec …/sudoforge/scripts/start-service` in `sway/config`), a float rule (`app_id=sudoforge`, border 3, focus) in `rules.toml`, Help page `15-passwords.md` on the Tools tab; live copies updated, `sway -C` valid, rules reloaded; service started by hand 21:22 (registered for session 2). `~/.local/bin/sudoforge` → `main.py`
- [x] Tests: **30 pass** (+1 live polkit check, `SUDOFORGE_LIVE_POLKIT=1`: a real `pkexec` from another program reached the box, cancelled, exit 126). Stand-in sudo (a process named sudo) + stand-in box: the password reaches sudo and never the log; cancel; only sudo may ask; wrong token gets nothing; one box at a time; no service → plain words; 0700/0600 + cleanup; a cancel closes an open box; sudo.conf on throwaway files

## Phase 2 · Javier's run, then release
- [ ] Test matrix in `testing/`; Javier's run (USB stick, printer, `sudo -A`, nog from the launcher, wrong password ×3)
- [ ] Release 1.0.0: tag `sudoforge-v1.0.0`, GitHub Release, AUR; close #26 and #24

## Later
- [ ] The keyring (saved logins for Claude Desktop, Chrome, Discord) — its own research (hypeForge D-61)
