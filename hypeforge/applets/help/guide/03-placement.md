# Window Placement (applet 2)

**What it does:** every new window goes to its spot by itself, in the same order in every
workspace (screen 1 = middle, 2 = left, 3 = right):

| Window | Goes to |
|---|---|
| 1 | screen 1, the whole screen |
| 2 | screen 1, beside window 1 |
| 3 | screen 2, the whole screen |
| 4 | screen 2, beside window 3 |
| 5 | screen 3, the whole screen |
| 6 | screen 3, beside window 5 |
| 7 | screen 2, under window 4 |
| 8 | screen 3, under window 6 |
| 9 and more | round the same order again, as **tabs** |

It counts everything you can see in the workspace, a shared screen included. Floating windows
and dialogs are left alone. You can always move a window by hand: **Win + Shift + arrows**, or
drag it with **Win + left mouse button**.

## Settings

`~/.config/hypeforge/applets/placement.toml`

- `enabled = true / false`
- `screens` — the screens in order
- `order` — the spots, as screen + `fill` / `right` / `under-right`

After editing by hand: `hypeforge-placement reload`.
