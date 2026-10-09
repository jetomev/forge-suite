# workspaceForge v1.0.0 — Test Results (9 Oct 2026)

On the test desktop (Arch, Sway 1.12, hypeForge, three screens).

| Area | Result |
|---|---|
| Automated | **33 PASS**, 0 warnings. 12 behaviours broken on purpose in a copy (one app one workspace, holds before renames, the backup, a rename keeping its apps, sharing left to the applet, one always stays, Select All = rows showing, one open at a time, quit asks, the applet told, the rename note, delete asks): **12 caught** |
| Pictures | every page at 100 × 30, checked by eye: three bugs found and fixed with tests (a rename counted as 7 changes; clashing renames when a screen starts sharing; clipped text) |
| Text console | a `TERM=linux` preview of each page: every character in the console font, none invisible |
| Hidden bench | `scripts/bench-save.py`: a screen-less Sway, the real Workspaces helper, five test windows; a rename + a swap + a delete saved through workspaceForge's own code: **every window followed its workspace**, the helper kept running, the screens steady — twice |
| Javier, first run (rows 1–8) | *"Workspaces works well."* *"Apps. Work well. Both tables should be at the same height"* → fixed the same hour (row 7). *"Sharing. Not working for me"* → off the menu (D-7) |
| Not run on the desktop yet | rows 9–12 (a saved app list opening for real, a live rename with windows, quit outside Settings, the installed package) — row 12 is the local package test before the AUR push |
| Not tried | one or two screens (a VM); a real text console (only the preview) |

Javier named it 1.0 (D-8): *"this is workspaceForge v1.0"*.
