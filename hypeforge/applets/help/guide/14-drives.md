# USB drives (applet 11)

**What it does:** plug in a USB stick, a USB disk or a disc, and it is **mounted by itself**
(opened for use) — a notification says so, and the **drives icon** on the bar (left of
Bluetooth) turns blue with the count of drives mounted.

## How to use it

**Click the drives icon** for the list, under the bar's right end:

- **Open** — the drive in Midnight Commander.
- **Eject** — safely unmount it and switch it off; a notification says when it can be
  unplugged (or that something is still using it).
- **Mount** — for a drive that is plugged in but not mounted.

Drives the system mounts on its own (like the **Backup** drive at `/mnt/backup`) show in the
list but are never offered for Eject.

## Safety

- **Internal drives are never mounted** by this — two of this computer's internal drives hold
  Windows.
- **Windows (NTFS) drives are mounted read-only**, even external ones: you can copy from them,
  not change them. A Windows drive that was hibernated can be damaged if it is changed from here.

## Settings

`~/.config/udiskie/config.yml` (udiskie does the mounting). Its notes explain each rule.
