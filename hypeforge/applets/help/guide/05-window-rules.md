# Window Rules (applet 5)

**What it does:** decides which windows **float** — small, centred, above the others — instead
of taking a spot. Sway already floats real dialogs (Save as…, file pickers); these rules catch
the small tools that do not call themselves dialogs: the calculator, Network Connections, Print
Settings, password windows, picture-in-picture video, Steam's side windows and more.

## How to use it

- **A click picks the window you work in.** Moving the mouse over a window doesn't select it; a click does (Win + arrow keys too).
- **Floating windows step aside.** In Sway a floating window is always drawn above the others, so when you click a window it covers, it is **tucked away** — like minimised. Its icon on the taskbar (dimmed while tucked) or **Win + −** brings it back on top. One beside the window you clicked stays; a dialog of the same app ("Save as…") never goes away.
- **Win + Shift + Space** floats a window, or puts it back in its spot. A floating window keeps its frame; to resize it, hold **Win** and drag with the **right** mouse button (Win + left button moves it).
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
