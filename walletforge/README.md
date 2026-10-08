<p align="center">
  <img src="../hypeforge/assets/kognogos-emblem.png" alt="KognogOS emblem" width="96">
</p>

<p align="center">
  <img alt="Status: in design" src="https://img.shields.io/badge/status-in%20design-f9e2af?style=flat-square&labelColor=313244">
  <img alt="Sway" src="https://img.shields.io/badge/for-Sway-89b4fa?style=flat-square&labelColor=313244">
  <img alt="License: GPLv3" src="https://img.shields.io/badge/license-GPLv3-a6e3a1?style=flat-square&labelColor=313244">
  <img alt="Built by a human and an AI" src="https://img.shields.io/badge/built%20by-human%20%2B%20AI-f9e2af?style=flat-square&labelColor=313244">
</p>

# walletForge

**The keeper of your saved logins on the KognogOS desktop.** Apps like Claude Desktop, Chrome and Discord need a safe place to keep you signed in between restarts. Plasma gives them KWallet, GNOME gives them Keyring; Sway gives them nothing, so they either forget you or keep your login in plain text. walletForge is that safe place, built for Sway and the Forge Suite.

## What it does

- **Answers the standard interface** apps already speak (the "Secret Service", `org.freedesktop.secrets`), so nothing in those apps changes.
- **Opens with your login password, at login.** You type your password once, at the login screen, and that is it. No second window.
- **Asks through sudoForge's box** only when it must (a locked store on a session that did not come through the login screen).
- **Keeps everything encrypted** on disk; the key is derived from your password and lives only in memory.

## Status

**In design, 2026-10-07.** Javier: *"I do not want to keep putting the password every time… it is like a critical functionality."* Research and decisions: [docs/research/](docs/research/) · [docs/DECISIONS.md](docs/DECISIONS.md) · the list: [TODO.md](TODO.md).

## License & credits

GPLv3. Built by Javier and Claude, part of the [Forge Suite](../). Thanks to the KDE team: KWallet and its PAM module showed the way the login password can open a store without being stored.
