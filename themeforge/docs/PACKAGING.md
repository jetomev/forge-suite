# themeForge — what the package needs

*Kept current with the code: `tests/test_needs.py` reads every import in `themeforge/` and fails when one
isn't listed here (Javier, 2026-10-11: "did you take notes of all of those dependencies … for the package?").
The AUR's `depends=()` is this table's Package column.*

| Package | What uses it | Module(s) |
|---|---|---|
| python | everything | (standard library) |
| python-textual | the app's screens | textual |
| python-rich | the half-block preview's colours | rich |
| python-forgekit (>= 0.10.0) | the Forge look, menus, manual, start check (ours, on the AUR) | forgekit |
| python-pillow | the previews: laying a picture on a screen, the half blocks, the overlay's picture | PIL |
| python-gobject | the full-quality preview (overlay.py) | gi |
| python-cairo | the overlay lets clicks pass through | cairo |
| gtk3 | the overlay's picture layer | gi: Gtk 3.0, Gdk 3.0, GdkPixbuf 2.0 |
| gtk-layer-shell | the overlay sits over the terminal as a desktop layer, not a window | gi: GtkLayerShell 0.1 |
| sway | where the overlay finds themeForge's window (its socket) | (Sway's IPC, standard library socket) |
| hypeforge | the look command themeForge drives (`hypeforge-theme`) | (runs it; not packaged yet: from the repo) |

## Optional

| Package | Why |
|---|---|
| alacritty | the launcher entry opens themeForge in it; any terminal works (the sharp preview needs one that tells its size: Alacritty, foot, kitty, Konsole do) |

## Only for the tests and benches (not the package)

grim, dbus, a GPU for `scripts/overlay-bench.py` (Alacritty won't start on the pixman renderer), hypeForge's `scripts/fake-keyboard.py`.

## hypeForge's own needs that themeForge relies on

hypeForge isn't packaged yet. When it is, its look command needs: python-pillow and python-numpy (the wallpapers: the drawn topics and the KognogOS backgrounds), swaybg (the wallpaper on screen), adw-gtk-theme (the GTK theme each look builds on, F-70), the icon and cursor themes the palettes name. Noted in hypeForge's TODO.
