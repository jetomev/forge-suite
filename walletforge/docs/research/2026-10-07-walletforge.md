# walletForge — research, 7 October 2026

*How Plasma opens the wallet with the login password, what Sway lacks, and what that means for our own store. Everything here was checked on the test desktop (Arch, Sway 1.12, kwallet 6.30, kwallet-pam 6.7.5) the same night.*

## The problem, in one line

Apps keep saved logins through a "secret store" (the standard **Secret Service** interface, D-Bus name `org.freedesktop.secrets`). Plasma starts one and unlocks it with the login password. Sway starts nothing, so Claude Desktop lost its login at every restart (#39), and once a store is started by hand, it asks for the wallet password in a KDE window at every login (#41).

## How Plasma does it (checked, not read)

1. **At the login screen**, the PAM module `pam_kwallet5.so` (listed in `/etc/pam.d/sddm`, `auth` and `session … auto_start`) hashes the typed password (PBKDF2, salt from `~/.local/share/kwalletd/kdewallet.salt`), **forks the wallet daemon** with the hash on a pipe — here `/usr/bin/ksecretd --pam-login 12 13` — and leaves a socket at `/run/user/1000/kwallet5.socket`, named in the session's environment as `PAM_KWALLET5_LOGIN`.
2. **The daemon waits** on that socket (seen: state sleeping in `__skb_wait_for_more_packets`, owning no bus names) until something sends it **the session's environment**: `/usr/lib/pam_kwallet_init` is just `env | socat STDIN UNIX-CONNECT:$PAM_KWALLET5_LOGIN`. Plasma runs it from the user unit `plasma-kwallet-pam.service`.
3. On receiving the environment, the daemon joins the session bus, owns `org.freedesktop.secrets`, `org.kde.ksecretd`, `org.kde.secretservicecompat`, the KWallet portal, and opens the wallet with the hash. **No window.**

## Why it did not happen on Sway

- Nothing sends the handshake. The daemon from step 1 sat waiting all evening (pid 3642 since 21:09).
- Running Plasma's unit by hand (`systemctl --user start plasma-kwallet-pam.service`) "started" and did nothing: **systemd's user environment does not carry `PAM_KWALLET5_LOGIN`** (`systemctl --user show-environment` has no such line), so the script saw an empty variable and exited.
- Sent **from the session** (`env | socat … /run/user/1000/kwallet5.socket`, 21:20), the waiting daemon woke within a second and took the bus names. The copy hypeForge had started by hand (`exec ksecretd`) stepped aside.

## What this means

- **For #41 (now):** hypeForge can send the handshake itself at login — `exec /usr/lib/pam_kwallet_init` in the Sway config has the variable, because Sway's `exec` runs in the session's environment. Then the wallet opens with the login password, and `exec ksecretd` is no longer needed. Proof: a reboot, Claude Desktop opens signed in, **no KDE window**.
- **For walletForge (the design):** the PAM module takes a `kwalletd=` option naming **which daemon to start**. So walletForge does not need its own PAM module: `pam_kwallet5` can fork **our** daemon with the password hash, and hypeForge sends the same handshake. Our daemon then answers the Secret Service interface with a store encrypted by a key derived from that hash. The salt file and the hash recipe are KWallet's (PBKDF2-SHA512, 56 bytes, 50,000 rounds, from the module's source); walletForge can use the same so the two can coexist during the move.
- **Fallback when no PAM hash arrived** (a session not started through the login screen, or a changed password): ask through sudoForge's box, never a blank password.

## Still to check

- The wallet password must equal the login password for step 3 to open it silently; if they differ, the daemon registers but stays locked (then KDE asks). Javier confirms which he typed tonight.
- Whether Chrome and Discord pick the store up the same way (Chrome: `chrome://version` shows the store in use).
- The exact bytes `pam_kwallet5` writes on the hash pipe, from its source, before walletForge's daemon reads them.
