# Files

- **The settings:** `~/.config/hypeforge/applets/workspaces.toml`, the Workspaces helper's own file. workspaceForge reads and writes it; you can also edit it by hand and run `hypeforge-workspaces reload`.
- **Backups:** `~/.config/workspaceforge/backups/`, one before every save; the last 20 are kept. To go back, copy one over the settings file and reload.
- **Screen names** come from displayForge (Identify), if you gave them names there.

## Inside hypeForge Settings

hypeForge Settings opens workspaceForge as its **Workspaces** page (started with `--hypeforge`). There it has no Quit of its own: Settings closes it, asking first if something isn't saved.
