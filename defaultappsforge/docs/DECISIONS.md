# defaultappsForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

## 2026-10-09

### D-4 · The design is approved (Javier)
*"Default Apps: a little space too between the titles and the info under them. WOW APP!!!!"* — the space added, and the open questions taken with the recommendations (Claude said "go" would take them; Javier may still change any):
1. An **Office Suite** default app (documents, spreadsheets, presentations), ONLYOFFICE today: fourteen in all.
2. **Terminal Emulator** through the `xdg-terminal-exec` standard (official repository, small): installed with nog when a terminal is chosen; hypeForge's Win + Enter follows the same choice.
3. **Phone Numbers** stays, its drop-down saying "none installed" until something handles them.
4. Old choices for apps that are gone are tidied away on save, shown in the review.
5. Each default app starts with its usual file types; the rest wait on the left of File Types.
6. Save is a pop-up review. 7. `~/.config/mimeapps.list`, a backup first. 8. A Default apps page and Home card in hypeForge Settings. 9. 0.1.0 → 1.0.0 after Javier's run.

### D-3 · Second design review: structure for Default Apps; File Types' tables aligned (Javier)
*"Default Apps looks disjointed. I think between lines there could be a little gap. Also, the dropdowns shouldn't be so far from the title. Maybe the title with a bullet point also will help give structure. On top of the list of default title, we are missing an underlined title: Defaults. On top of the options drop downs, an underlined title: Selection."* File Types: *"good. Remember both tables to be aligned from the top."* Third draft the same hour.

### D-2 · First design review: his thirteen default apps with drop-downs; File Types like workspaceForge's Apps page (Javier)
1. **Kinds → Default Apps:** Web Browser · Email Client · Calendar · Phone Numbers · Image Viewer · Music Player · Video Player · Text Editor · PDF Viewer · File Manager · Terminal Emulator · Archive Manager · Map. A drop-down next to each with the apps available. *"No need for status, it is kind of overkill."*
2. **File Types:** *"kind a busy section."* The most common types only, assigned to the default apps (to keep it simple), done like workspaceForge's Apps page: file extensions on the left, the default apps on the right each with its own types, `>>` to assign, `<<` to clear.

Second draft the same hour. New questions from what it needs: Office Suite (documents have no default app in the list), the Terminal Emulator standard (`xdg-terminal-exec`, not installed), Phone Numbers with nothing installed.

### D-1 · defaultappsForge is next, and its name (Javier)
Picked after nightForge: *"dappsForge next? (default apps)"*, then *"d-appsForge"*, then *"ah! wait, then defaultappsForge"* — Claude had pointed out that "dApps" is a crypto word, and that Python names can't hold a hyphen. It is the Forge app #19 (F-36, 2026-09-30) has been waiting for; the stopgap `handlr-regex` stays meanwhile. The design first, for his approval.
