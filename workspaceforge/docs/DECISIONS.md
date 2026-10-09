# workspaceForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

## 2026-10-09

### D-6 · 0.1.0 stops at nine workspaces (Claude, told to Javier)
The approved answer 1 (D-5) was *as many as you like; Win + 1 … 9 reach the first nine*. Building it showed the Workspaces applet names each screen's part of a workspace `<n + 10 × screen>:<name>`, which only works up to nine: a tenth would clash with the second screen's first. Changing that naming renames every workspace on the desktop, so it gets its own step with its own bench test. **0.1.0 allows one to nine** and says so on screen ("9 is the most for now"); more than nine is in the TODO.

### D-5 · The design is approved (Javier)
*"approved!!!!"* — the third draft (`docs/design/v0.1.0-screens.html`), with the eleven open questions answered by the recommendations, as Claude said they would be unless he changed any:
1. As many workspaces as you like; Win + 1 … 9 reach the first nine, the rest from the bar's list; at least one always stays.
2. One app, one workspace (the two tables already work that way).
3. The apps table's filters: Find and Category; headings sort (▲ ▼).
4. Sharing: one shared group per screen (every cell switched to Shared in a column).
5. "Select All / Deselect All" everywhere; nogForge's "Tick All / Untick All" follows in its next release.
6. Deleting a workspace asks where its windows go (Daily preselected); nothing is ever closed.
7. The app lists start from the launcher's groups, once; after that the lists are the one place this is set, and the launcher follows them.
8. F10 shows a review, then applies at once; no countdown (nothing here can black out a screen).
9. hypeForge's Workspaces applet does the work; workspaceForge only edits its settings and asks it to re-read.
10. A "Workspaces" page in hypeForge Settings opens workspaceForge (`--hypeforge`).
11. 0.1.0 while it is built; 1.0.0 when the whole design works and Javier has run it.

**Next:** the engine (F-50, #55) in the Workspaces applet, then the app.

### D-4 · Second design review: buttons on top, new and edit in place, sharing as switches (Javier)
1. **Workspaces:** the New / Edit / Delete buttons go **on top**, not below; Move Up / Move Down on top of the list. **New** needs no pop-up: the same page, a blank form. **Edit** happens on the same page, no pop-up; after a rename, the apps line turns yellow with a small ⚠, asking to review the apps assigned on the Apps page; **not persistent**, just a message after the rename. **Delete** keeps its warning pop-up.
2. **Apps:** *"perfect."*
3. **Sharing:** *"Don't understand how the sharing works. How do you select a screen and tell it where it is shared."* → the same table, but an input in every cell to switch between Shared and not, and a Save button at the bottom.

Third draft drawn the same morning. Claude's reading, put to Javier as a question: every cell switched to Shared in one column shares that screen together, so each screen has at most one shared group.

### D-3 · First design review: workspaces are dynamic; Apps is two tables with arrows (Javier)
1. **Workspaces are dynamic:** *"If the user just want to have one, they only have one."* Create, name, edit and remove them as you please; no fixed set.
2. **Apps, simpler:** on the left, the apps and their category in a vertical table, our table formatting, a `[x]` next to each name, Select All / Deselect All on top. On the right, the workspaces; clicking one expands it downward to show its apps (the previously open one retracts); its apps have `[x]` too, with Select All / Deselect All on top. **Both act only on the rows showing**, never on every workspace.
3. **Between the tables:** `>>` sends the ticked apps from the list to the open workspace; `<<` sends the ticked apps of the open workspace back to the list.

Second draft drawn and published the same morning. The "Add an app" search window of the first draft is gone (the left table and its filters replace it).

### D-2 · Workspaces only; windows are another Forge app (Javier)
*"Notice I said only workspaces, windows is another Forge app. I like atomized solutions."* The Settings catalogue had one area, "Workspaces & Windows" (hypeForge D-66). It is two apps: **workspaceForge** (names and order, which apps open where, sharing) and, later, a separate Forge app for where windows sit on a screen and which ones float (today's Window Placement and Window Rules applets).

### D-1 · workspaceForge is born, now (Javier)
*"You know what, now that we are at it. Why don't we work on workspaceForge already. It is HOT topic xD"* — right after F-50 (#55): apps should open on their own workspace however they are started, set from per-workspace lists. Those lists need a place to be edited; workspaceForge is that place, and the rest of the workspace settings come with it. A new section of the Forge Suite (D-60), own version and tags. First step: the design, screen by screen, for Javier's approval.
