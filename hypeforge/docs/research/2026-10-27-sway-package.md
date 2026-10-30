# Our Sway build as a KognogOS package — a draft (2026-10-27)

*TODO Phase 12: "Our Sway build as a KognogOS package (D-111): today it's built in the home folder; the disc
needs a package (KognogOS 1.0)". Done by Claude overnight on Javier's "do everything you can do by
yourself"; nothing installed. The choices at the bottom are Javier's.*

## What was made

`sway-hypeforge/PKGBUILD`: the same steps as `build.py`, as a package.

- Source: Sway's release tarball from github.com/swaywm/sway plus its `.sig`, checked against Simon Ser's
  release key (`validpgpkeys`), our five patches applied in order (`0001`…`0005`).
- Built with Arch's own settings (`arch-meson`), man pages off, installed to **`/opt/sway-hypeforge/`**:
  only `bin/` (sway, swaymsg, swaybar, swaynag) and the licence. The wallpapers, shell completions and
  `/etc/sway/config` are the system Sway's and are left out, so the two packages share no file.
- `depends` = what Arch's `sway 1:1.12-4` depends on (wlroots0.20 and the rest) plus `sway>=1:1.12` itself.

## How it was checked

| Check | Result |
|---|---|
| `makepkg -Cf` in the scratchpad (`BUILDDIR`, `PKGDEST`, `SRCDEST` outside the repo) | built: `sway-hypeforge-1.12-1-x86_64.pkg.tar.zst`, 5.4 MB |
| Every file in the package against `pacman -Qo` | no file owned by another package |
| `/opt/sway-hypeforge/bin/sway --version` (from the unpacked package) | `sway version 1.12` |
| `sway -C` on this login's `hypeforge-config-buttons` | packaged Sway: valid (exit 0) · stock Sway: rejects it (exit 1), as expected — the button lines are ours |
| `scripts/titlebar-paint-bench.py --sway <packaged>` | 2/2 |
| `scripts/winkey-bench.py --sway <packaged>` | 8/8 |

Found on the way: Sway 1.12's meson refuses `sd-bus-provider=auto` when every feature is switched on (as
`arch-meson` does): `-Dsd-bus-provider=libsystemd`, as Arch's own Sway package sets it.

Not checked: installing it (`nog install`), a login through it, the session starter finding it (it looks
only in `~/.local/opt` today, see 3 below), `login-test.sh` in a VM.

## The choices (Javier's)

*2026-10-30: 1 → KognogOS's own source only (D-127); 2 → the hold, `sway=` (D-128); 3 → done and proven in the VM (`testing/20261030 - Test Results for hypeForge's Sway package 1-12.md`); 4 still open.*

1. **Where it's published.** The KognogOS package source for the disc (stage 05's repository) — or the AUR
   too. *Claude's lean:* the disc's own source first; the AUR only if someone outside KognogOS asks, since
   it's useful only with hypeForge's config.
2. **How it follows a Sway update.** `sway>=1:1.12` (as drafted): when Arch moves to 1.13 the update goes
   through, our build is one version behind, and the login falls back to the system's Sway (no buttons, one
   notice) until we rebuild — his 10-17 rule, *"whenever sway updates, it does not brake our system"*. The
   other way, `sway=1:1.12`, would hold Sway's update back until ours is ready (no fallback ever, but a stuck
   system update). *Claude's lean:* `>=`, as drafted.
3. **The login starter** (`hypeforge-session`) looks only in `~/.local/opt/sway-hypeforge/current`. It needs
   to try `/opt/sway-hypeforge/bin/sway` first. A small change, but it's the login path: changed only with
   `login-test.sh` run in the VM first. Not touched tonight.
4. **Who owns the login entries** (`hypeforge.desktop`, `hypeforge-safe.desktop`, installed by hand into
   `/usr/share/wayland-sessions/` today). *Claude's lean:* hypeForge's own package owns the entries and the
   starter; `sway-hypeforge` only the program.
