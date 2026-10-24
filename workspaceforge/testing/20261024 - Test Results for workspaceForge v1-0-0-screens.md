# Test Results — workspaceForge v1.0.0 on one and two screens, and a text console

*2026-10-24 · Javier's run of [the matrix](20261024%20-%20Test%20Matrix%20for%20workspaceForge%20v1-0-0-screens.md) on the desktop: NVIDIA RTX 3060, three Sceptre Y27 (2560 × 1440), Sway (hypeForge). Screens switched off with displayForge (the code on `main`, Try + Keep, never saved). The installed workspaceForge 1.0.0.*

**Result: PASS — every row. No findings.**

| # | What | Result |
|---|---|---|
| C1 | The save on one, two and three hidden screens (`bench-save.py --screens`) | ✅ (Claude) |
| C2 | Screens off and on under the applet (`hypeforge/scripts/screens-off-bench.py`) | ✅ (Claude) |
| C3 | The app drawn with one and two screens | ✅ (Claude) |
| C4 | No Sway at all: the start-up check | ✅ (Claude) |
| A1–A5 | Two screens: one off, its windows moved over, Win + 1…4 switch both together, workspaceForge reads right, a rename (Gaming → Play) shows on both | ✅ all five (Javier) |
| B1–B4 | One screen: everything on it, the workspace keys work; Daily's line "switches all your screens" with one screen — **Javier: "fine as it is"** | ✅ all four (Javier) |
| C5–C7 | All three back on, workspaces back on their screens, the rename undone | ✅ (Javier); checked after: DP-2 0 · DP-3 2560 · DP-1 5120, all at 100 %, "Gaming" in the file |
| D1–D3 | A text console: the start-up check, Continue Anyway readable, back to the desktop | ✅ (Javier) |
