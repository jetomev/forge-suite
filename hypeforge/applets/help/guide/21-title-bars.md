# Title bars and the window menu

**What it does:** every **floating** window (one you lifted out of the grid, a dialog, a small Forge
app) gets a **title bar** in your look's colours and font. Tiled windows keep their clean frame, so
the grid keeps its room. Apps that draw a bar of their own (GNOME's apps, Claude Desktop) keep
theirs, and ours doesn't show on them.

## How to use it

On a floating window's title bar:

- **Press and drag** (left button): move the window anywhere.
- **Middle click**: tuck it away (minimise). The **tucked windows icon** on the bar, or **Alt + Tab**,
  brings it back.
- **Right click**: the **window menu**, right under the title bar:
  - **Float** / **Back into the grid** — lift a tiled window out, or put a floating one back.
  - **Full screen**, and **Show on every workspace** (a floating window).
  - **Move to workspace ▸** — every workspace by its name; the one it's on is marked.
  - **Tuck away** and **Close**.
  - **Esc** or a click outside closes the menu.

Tiled windows move as before: **Win + left mouse button** drags them in the grid, **Win + right mouse
button** resizes. **Win + Shift + Space** floats a window or puts it back.

## The buttons (the "Sway (hypeForge buttons)" login)

On hypeForge's own Sway build, a floating window's title bar also has **─ □ ✕** at its right:
**─** tucks it away, **□** fills the screen (click again: back where it was), **✕** closes it. If Sway
was updated and our build is out of date, that login starts the normal Sway instead — everything
works, the buttons are off, and a notification says so until it's rebuilt.

## Good to know

- A window that floats by itself (a dialog, a window rule, the menu, the keys) gets the title bar
  however it got there; back in the grid it loses it.
- **Chrome** can use our title bar: Settings → Appearance → **Use system title bar and borders**.
  Apps whose bar can't be switched off keep their own.
