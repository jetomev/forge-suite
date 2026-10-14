# hypeForge — what the package needs

*Measured from the code on 2026-10-11 (Javier: "check all Forge Suite apps for all dependencies needed to build and
run them"), with the Forge Suite's audit, `forge-suite/scripts/needs-audit.py`, and proven by building the
AUR recipe in a clean Arch system (devtools' `makechrootpkg`, tests included). `tests/test_needs.py` reads every import and fails when one isn't listed here, so this page can't fall behind the code.
Arch's `base` packages (bash, coreutils, glibc, sed, grep, util-linux, systemd…) are on every Arch install and
aren't listed.*

## Needs (the recipe's `depends`)

| Package | What uses it | Module / program |
|---|---|---|
| python | the applets | — |
| sway | the desktop itself (swaymsg, swaynag) | (programs) |
| swaybg | the wallpaper on screen | (Sway's output bg) |
| waybar | the bar | (program) |
| mako | notifications (makoctl) | (programs) |
| fuzzel | the launcher and the lists | (program) |
| gtklock | the lock screen | (program) |
| swayidle | locking when idle | (program) |
| python-gobject | the pop-up panels | gi |
| gtk3 | the pop-up panels | gi: Gtk 3.0, Gdk 3.0 |
| gtk-layer-shell | the panels sit on the desktop's layers | gi: GtkLayerShell 0.1 |
| python-textual | Help & Keys, hypeForge Settings | textual |
| python-rich | the same | rich |
| python-forgekit | the same | forgekit |
| python-pillow | the look command: wallpapers, the lock picture | PIL |
| python-numpy | the wallpaper drawings (generate.py) | numpy |
| adw-gtk-theme | the GTK theme every look builds on (F-70) | — |
| wl-clipboard | the clipboard (wl-copy, wl-paste) | (programs) |
| cliphist | clipboard history | (program) |
| grim | screenshots | (program) |
| slurp | picking an area for a screenshot | (program) |
| swappy | editing a screenshot | (program) |
| libnotify | messages from the applets (notify-send) | (program) |
| networkmanager | network (nmcli) | (program) |
| networkmanager-dmenu | the network list | (program) |
| wireplumber | volume (wpctl) | (program) |
| libpulse | volume keys (pactl) | (program) |
| bluez-utils | Bluetooth (bluetoothctl) | (program) |
| udisks2 | USB drives (udisksctl) | (program) |
| udiskie | mounting drives at login | (program) |
| cups | printers (lpstat, cancel) | (programs) |
| playerctl | the media keys | (program) |
| xdg-user-dirs | where screenshots go | (program xdg-user-dir) |
| xdg-utils | default apps (xdg-mime) | (program) |
| alacritty | the terminal | (program) |
| thunar | the file manager | (program) |
| nightforge | the night light (its code is imported by the moon) | nightforge |
| sudoforge | password boxes | (program) |
| nog | packages | (program) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| glib2 | telling GTK apps the new look (gsettings) | (program gsettings) |
| wlsunset | the night light without nightForge | (program) |
| ddcutil | the brightness keys on desktop monitors (DDC/CI, displayForge's channel; #94) | (program) |
| brightnessctl | the brightness keys on a laptop's screen (a backlight in /sys/class/backlight; #94) — optional on a desktop | (program) |
| kwallet-pam | `/usr/lib/pam_kwallet_init`, run at login: KDE's saved-passwords store opens with the login password, no window (#39, #41) — until walletForge | (file, not on PATH) |

## The AUR recipe

No package yet: KognogOS installs these. When hypeForge gets its package, this is its list.

## Found by the audit

- ~~brightnessctl isn't installed, but Sway's config binds the brightness keys to it~~ — **done 2026-10-13 (#94, D-99):** the keys run `applets/brightness/hypeforge-brightness`, which uses the backlight when there is one (brightnessctl) and the monitors' own control when there isn't (ddcutil), both listed above.
- ~~pam_kwallet_init isn't on this system~~ — **the audit was wrong (#95):** it is there, `/usr/lib/pam_kwallet_init` from kwallet-pam 6.7.5, and the login's PAM (`/etc/pam.d/sddm`) starts the store for it; the audit looked it up on PATH, where /usr/lib never is. The line works, and it is what keeps the KDE password window away (#41). Listed above as a need, until walletForge.
- **The wallpaper generator lives in docs/** (`docs/research/look-2026-10/wallpapers/generate.py`) but the look command runs it: a runtime piece in a research folder. Move it under `applets/theme/`.
