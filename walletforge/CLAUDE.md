# walletForge — section rules

*A Forge Suite app (D-60): KognogOS's own secret store for the Sway desktop. Read the suite's `CLAUDE.md` first; this file adds what is particular here.*

- **What it is:** the place apps keep their saved logins and keys (what KDE calls KWallet and GNOME calls Keyring), answering the standard "Secret Service" interface (`org.freedesktop.secrets`) so Claude Desktop, Chrome, Discord and every libsecret app work unchanged. Unlocked by the **login password at login**, never asked again; asked through **sudoForge's box** only when it has to be.
- **Decisions** live in `docs/DECISIONS.md` (D-1…); research in `docs/research/`. Read them before changing the design.
- **Safety first:** secrets are encrypted at rest; the key never touches a log; a blank password is never an option; nothing of the user's is read or written before the design's unlock path is proven.
- **Tests:** `python -m unittest discover -s tests -v` (stdlib runner). Report the test count at every release; the store is exercised through the real D-Bus interface with `secret-tool` in the failing direction too (locked, wrong key, no session).
- **Versioning:** own version, tags `walletforge-vX.Y.Z`, AUR `walletforge` when it ships. Plain words everywhere; the readers are not engineers.
