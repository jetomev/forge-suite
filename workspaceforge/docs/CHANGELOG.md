# workspaceForge — changelog

*Newest first.*

### 1.0.0 — October 9, 2026 · your workspaces, in the terminal ([#56](https://github.com/jetomev/forge-suite/issues/56))

Born, designed, approved, built and run in one day. The design went through three drafts with Javier (D-3, D-4) and was approved (D-5); he named this first release 1.0 (D-8).

- **Workspaces:** your workspaces with the Win key that reaches each, the one on screen marked. Buttons on top: **New** and **Edit** right on the page, no pop-ups; a short yellow ⚠ note after a rename asks you to check the workspace's apps; **Delete** asks first and moves the open windows to a workspace you pick (nothing is ever closed); **Move Up / Down** changes the Win numbers. The switch for all screens together, or each screen by itself.
- **Apps:** which apps open on each workspace, however they are started (the engine is hypeForge's F-50, #55). The apps on no workspace on the left (ticks, category, shaded rows, headings that sort, Find + Category), the workspaces on the right (one open at a time), **>>** and **<<** between them. Select All / Deselect All act only on the rows showing.
- **Saving:** **F10** shows a review, makes a backup (the last 20 kept), carries the open windows along to their workspace's new name or place, writes the file (it must read back the same) and asks hypeForge's Workspaces helper to read it at once. Quitting with something unsaved asks.
- **Inside hypeForge Settings** as its Workspaces page (`--hypeforge`: no Quit of its own). A five-part manual (Help → Manual).
- **Not in 1.0:** Sharing (a screen keeping the same apps across workspaces) is off the menu while Javier rethinks it (D-7); saving keeps whatever the file says about it. **Nine workspaces is the most for now** (D-6).
- **Found and fixed before release**, by looking at pictures of every page: a rename counted its apps as changes; a screen starting to share planned clashing renames; clipped text. After Javier's first run: the Apps page's two tables now start and end on the same lines.
- Tests: **33** (the model 18, the pages 15); 12 behaviours broken on purpose, all 12 caught. Warnings: 0. The save tested on a hidden Sway with the real Workspaces helper (`scripts/bench-save.py`: a rename, a swap and a delete, every window followed its workspace).
