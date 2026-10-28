# Why Waybar crashed — every recorded crash, sorted (2026-10-27)

The open half of F-82: *"15 crashes 10-10…10-22 (SEGV and ABRT) … read the next few and find the pattern"*.

## What was run

```
coredumpctl list waybar --no-pager
coredumpctl info <pid> --no-pager      # for each one still on disk: its signal, si_code and stack
```

## What the 25 records are

| When | Count | Signal | Where it died | What it was |
|---|---|---|---|---|
| 10-10 21:40, 21:44 | 2 | ABRT | (core gone) | the D-86 days: one Waybar per screen; GApplication's one-instance check aborted the extra copies on a reload (D-86's own note) |
| 10-17 15:09, 15:12 | 2 | SEGV (MAPERR) | `libdbusmenu-glib` | **Waybar's own tray** opening an app's menu. Replaced by hypeForge's own tray the same evening (D-103): Waybar's tray module isn't placed on any bar since |
| 10-17 22:23 – 22:24 | 6 | ABRT (TKILL) | `libgio` (GApplication) | six starts in 45 s, each aborted: a second Waybar started while one ran (GApplication, as on 10-10). One bar program for every screen (D-86, redone) and start/stop/guard sharing one lock (D-115) |
| 10-22 17:35:25 | 1 | SEGV (MAPERR) | `waybar + 0x6bda5` | 3 s after login: the login reload race, the same shape as 10-25 and 10-26 (the guard's records show "Reloading..." ~1 s after start while WirePlumber was starting). **F-86** (#130, fixed 3556cd8, proven at the 10-27 login) |
| 10-22 17:54 – 10-26 22:20 | 14 | SEGV (**SI_USER**) | `g_application_run` (killed while idle) | **not crashes**: `scripts/bar-guard-bench.py` and the sound-reload bench killing their own test bars on purpose (a signal *sent*, `si_code: SI_USER`) |

(10-25 18:52 and 10-26 19:35 left no core: the sound piece's abort path; their logs are in `~/.local/state/hypeforge/logs/bar-crashes/`, read for F-86.)

## The answer

Every real crash on record has a known cause, and each cause is gone: Waybar's tray (replaced, D-103), two Waybars at once (one program, D-86; one lock, D-115), and a reload while sound starts (F-86). None since the 10-27 fix. The bar guard (D-115) stays: it is what made the last two visible at all.

**For the future:** a bench-made kill shows `si_code: SI_USER` in `coredumpctl info`; anything else is real and worth a look.
