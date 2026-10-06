# Window Rules (applet 5)

**What it does:** decides which windows **float** — small, centred, above the others — instead
of taking a spot. Sway already floats real dialogs (Save as…, file pickers); these rules catch
the small tools that do not call themselves dialogs: the calculator, Network Connections, Print
Settings, password windows, picture-in-picture video, Steam's side windows and more.

## How to use it

- **Win + Shift + Space** floats a window, or puts it back in its spot.
- **Win + left mouse button** drags it, **Win + right mouse button** resizes it.
- **Win + Shift + Tab** switches the focus between floating and tiled windows.

## Settings

`~/.config/hypeforge/applets/rules.toml`

- `enabled = true / false`
- one `[[float]]` block per rule, matching on `app_id`, `class`, `title`, `window_role` or
  `window_type`; options `sticky = true` (shows on every workspace) and `size`

A window's names: run `swaymsg -t get_tree` while it is open. After editing:
`hypeforge-rules reload` (switching a rule *off* needs **Win + Shift + C** as well).

The **passphrase box** for your signing key (pinentry) floats too, centred with a light border.
