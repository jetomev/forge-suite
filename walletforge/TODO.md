# walletForge — the list

**Target: before KDE leaves the desktop (hypeForge's last step) — started 7 Oct 2026; design D-2 agreed the same night; not urgent, since the login password already opens KDE's store on Sway (#41).** The keeper of saved logins on the Sway desktop: answers the standard secret-store interface, opens with the login password at login, asks through sudoForge's box only when it must. Section of the Forge Suite (D-60). Updated after every step.

## Phase 0 · Research and design
- [x] Name: **walletForge** (Javier, 2026-10-07; D-1)
- [x] Research: how Plasma opens the wallet with the login password — `pam_kwallet5` hashes it, forks the daemon with the hash, leaves a socket; the session sends its environment to wake it; the module's `kwalletd=` option can name **our** daemon → `docs/research/2026-10-07-walletforge.md` (2026-10-07, checked live)
- [ ] Research: what the standard interface needs from a server (sessions with encryption, collections, items, prompts, aliases; what libsecret and Chromium actually call)
- [ ] Decide the store format and the encryption (key from the password hash PAM hands over; per-item encryption; the salt file)
- [x] Design, first pass approved (D-2, 2026-10-07): nothing on screen normally; a small Forge app to look / delete / lock; sudoForge's box when a password is needed; **SSH keys + GPG in scope (after the store); copy KDE's entries at the switch**; not urgent — after the daily-use items, before KDE leaves
- [ ] Research: KDE's wallet file format (`kdewallet.kwl`, encrypted with the same PBKDF2 hash) so the entries can be copied over at the switch
- [x] The stopgap meanwhile (#41): hypeForge sends the PAM handshake at login (`exec /usr/lib/pam_kwallet_init`) — wallet opened with the login password, no window — **proven after a reboot 21:26 (#41 closed)**

- [ ] **The password manager screen (Javier, 2026-10-07, from the Settings spike: "like the password administrator of Google Chrome")**: walletForge's own page in hypeForge Settings — saved logins by app, view / delete / lock, never showing a secret in plain text unless asked and unlocked. Until then the Settings "Passwords" page shows sudoForge's status

## Phase 1 · Build
- [ ] The daemon on the bus, the store on disk, tests through the real interface
- [ ] Unlock at login through PAM; sudoForge's box as the fallback
- [ ] hypeForge: started with the session (replaces `exec ksecretd`); Claude Desktop, Chrome and Discord proven to keep their logins across a reboot

## Phase 2 · Javier's run, then release
- [ ] Test matrix on the desktop; release 1.0.0; AUR `walletforge`; KognogOS disc list
