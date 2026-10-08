# walletForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

### D-2 · Scope, migration and timing (Javier, 2026-10-07 night)
- **Scope:** the store answering the standard interface, plus a small Forge app to look, delete and lock — **and SSH keys and GPG passphrases belong in it too**, "to maintain consistency in our system" (Javier). They come after the store works; the sudoForge pinentry (GPG asking in our box) is the natural first of those.
- **Migration:** when walletForge replaces KDE's store, **it copies the existing entries over** from KDE's wallet files, so no app asks to log in again (Javier: "copy the keys from KDE files").
- **Timing:** not urgent — the no-window goal is already met with KDE's store through the PAM handshake (hypeForge #41). walletForge moves back down hypeForge's order, after the daily-use items and before KDE is removed, which it must precede. Claude's recommendation, Javier's agreement.
- **Unlock:** the login password through `pam_kwallet5` starting our daemon; sudoForge's box when a password is needed anyway; a blank password never.

### D-1 · walletForge is a Forge Suite section; the name is Javier's (2026-10-07)
Javier, 2026-10-07: *"We are using KDE Wallet… we need a Forge Suite Wallet, don't you think?"* and later: *"let's start with walletForge, I do not want to keep putting the password every time, doesn't make sense to me, it is like a critical functionality."* Born as `walletforge/` in the Forge Suite (D-60), own version and AUR package. It is the hypeForge D-61 "keyring" step, pulled to the front of the ranked order.
