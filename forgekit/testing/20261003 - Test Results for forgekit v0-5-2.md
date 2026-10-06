# forgekit v0.5.2: Test Results (2026-10-03)

**The change:** the bottom bar shows the keys of the screen on show. Found by Javier in nogForge (Update → Dashboard kept Update's keys): a screen with nothing to select left focus in the screen just hidden, and the bar read that screen's keys.

| Check | Result |
|---|---|
| forgekit tests | **52 pass** (51 → 52); the new one fails without the fix (`'quiet keys' not found in ' x busy keys'`) |
| Every screen of every app, switched through in both directions, old vs new forgekit | old: grubForge, alacrittyForge, bitlaForge, nogForge all **inconsistent** on their first screen · new: all four **consistent** |
| The apps' own tests on 0.5.2 | grubForge 53 · alacrittyForge 80 · bitlaForge 64 · nogForge 33: all pass |
| Text console (`tools/console-preview.py`, the gallery) | every character in the console font and visible |
| Javier's own check | the AUR install, then any app: the bar changes with every screen (pending) |
