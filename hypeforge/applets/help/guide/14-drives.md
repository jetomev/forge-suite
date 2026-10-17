# USB drives (applet 11)

**What it does:** plug in a USB stick, a USB disk or a disc, and it is **mounted by itself**
(opened for use) — a notification says so. On the **Linux rice** look, the **disk piece** on the
bar (the drive icon with a percentage) turns blue while a USB drive is mounted; on the other looks,
the **drives icon** (left of Bluetooth) does, with the count of drives mounted.

## How to use it

**Click the disk piece** (or the drives icon) for the **Disks** pop-up, under the bar:

- **Click a disk** — it opens in the file manager.
- **Eject** — on a USB drive: safely unmount it and switch it off; a notification says when it
  can be unplugged (or that something is still using it).
- **Mount** — under **USB drives**, for a drive that is plugged in but not mounted.
- Every disk shows how much room is free (see *The system on the bar*).

Drives the system mounts on its own (like the **exodos** drive at `/mnt/exodos`) show as
"mounted by the system" and are never offered for Eject. A **right click on the drives icon**
still opens the plain list (Open in Midnight Commander · Eject · Mount).

## Safety

- **Internal drives are never mounted** by this — two of this computer's internal drives hold
  Windows.
- **Windows (NTFS) drives are mounted read-only**, even external ones: you can copy from them,
  not change them. A Windows drive that was hibernated can be damaged if it is changed from here.

## Settings

`~/.config/udiskie/config.yml` (udiskie does the mounting). Its notes explain each rule.
