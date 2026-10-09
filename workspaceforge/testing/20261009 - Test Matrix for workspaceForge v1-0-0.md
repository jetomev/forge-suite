# workspaceForge v1.0.0 — Test Matrix (9 Oct 2026)

On the test desktop (Arch, Sway 1.12, hypeForge, three screens). Start: `hypeforge-settings` → Workspaces, or `workspaceforge` once installed.

| # | Area | Do | Expect |
|---|---|---|---|
| 1 | Open | Settings → Workspaces | the six workspaces, ● on the one on screen; no Quit in the menu (inside Settings) |
| 2 | New | n, type a name, Enter | a "(new)" line, a blank form on the page, no pop-up; the bar counts 1 change |
| 3 | Edit | e, change the name, Enter | renamed on the page; a yellow ⚠ note about its apps, gone when another workspace is picked |
| 4 | Delete | d on a workspace with windows | a window lists them and asks where they go; Esc stays |
| 5 | Move | + / - | the order and the Win numbers change |
| 6 | Apps | 2; filter Utilities; tick one; open Gaming; >> | the app moves to Gaming's list; << sends it back |
| 7 | Apps layout | 2 | both tables start and end on the same lines |
| 8 | Save | F10 | a review (before → after), Save; the bar clears; "nothing changed yet" |
| 9 | Saved for real | after 6 + 8: start that app from a terminal | it opens on Gaming, every screen goes there |
| 10 | Rename live | rename a workspace with windows, F10 | its windows stay with it; Win + its number still works |
| 11 | Quit | change something, Q (outside Settings) | "Save your changes before quitting?" Yes / No / Stay |
| 12 | Installed | `nog install ./workspaceforge-1.0.0-1-any.pkg.tar.zst`; `workspaceforge` | starts; About says 1.0.0 |
