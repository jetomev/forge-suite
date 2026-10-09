# Forge Suite — repository rules

*One repository for every Forge app (D-60). Each app is a section with its own `CLAUDE.md`, `TODO.md`, `docs/DECISIONS.md` — read the section's own rules before working in it.*

- **Sections:** `hypeforge/` (the desktop), `displayforge/` (screens, 1.1.0), `forgekit/` (the foundation, 0.10.0), `sudoforge/` (passwords, 1.0.1), `walletforge/` (saved logins, in design since 2026-10-07), `workspaceforge/` (workspaces, 1.0.0). Shipped apps move in one at a time (alacrittyForge, bitlaForge, nogForge, grubForge last); **nog and mindForge stay their own repositories** (Javier, 2026-10-05).
- **Every app keeps its own version, tags `<app>-vX.Y.Z` and AUR package.** Release rules are adapted when the first shipped app moves in.
- **New Forge apps are born here**, as a new section — never a new repository.
- **The commit hook** runs each section's checks: `git config core.hooksPath hypeforge/scripts/hooks`.
- Commits name their section: `feat(hypeforge/…): …`. Co-author trailer on every commit; every commit signed.
- Plain words throughout; the readers are not engineers.
