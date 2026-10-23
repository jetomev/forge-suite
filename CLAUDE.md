# Forge Suite — repository rules

*One repository for every Forge app (D-60). Each app is a section with its own `CLAUDE.md`, `TODO.md`, `docs/DECISIONS.md` — read the section's own rules before working in it.*

- **Sections:** `hypeforge/` (the desktop), `displayforge/` (screens, 1.1.1), `forgekit/` (the foundation, 0.10.0), `sudoforge/` (passwords, 1.0.1), `walletforge/` (saved logins, in design since 2026-10-07), `workspaceforge/` (workspaces, 1.0.0), `nightforge/` (the night light, 1.1.0), `defaultappsforge/` (which app opens what, 0.1.0), `themeforge/` (the look, 0.1.0, since 2026-10-11), `alacrittyforge/` (Alacritty's settings, 1.1.1, moved in 2026-10-22), `bitlaforge/` (solo mining, 1.1.1, moved in 2026-10-22). Shipped apps move in one at a time (nogForge next, grubForge last); **nog and mindForge stay their own repositories** (Javier, 2026-10-05).
- **Every app keeps its own version, tags `<app>-vX.Y.Z` and AUR package.** How one ships, step by step: `docs/RELEASE-RECIPE.md` (release files from `scripts/release-app.sh`, reproducible since 2026-10-22).
- **New Forge apps are born here**, as a new section — never a new repository.
- **The commit hook** runs each section's checks: `git config core.hooksPath hypeforge/scripts/hooks`.
- Commits name their section: `feat(hypeforge/…): …`. Every commit signed.
