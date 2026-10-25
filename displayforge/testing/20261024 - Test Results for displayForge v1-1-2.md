# Test Results — displayForge v1.1.2 (stage 03: one and two screens, 80 / 90 %, a text console)

*2026-10-24 · Javier's run of [the matrix](20261024%20-%20Test%20Matrix%20for%20displayForge%20v1-1-2.md), the code on `main` (F-8, F-9, F-10). The test VM `kognog-hypeforge` (snapshot `screens-test-before` first) in virt-viewer; the desktop: NVIDIA RTX 3060, three Sceptre Y27 (2560 × 1440), Sway (hypeForge, KDE style · Dark Blue).*

**Result: PASS — every row, after one finding fixed during the run (F-10); the installed package passed at 1.1.4, after F-11 and F-12 (below).**

| # | What | Result |
|---|---|---|
| C1 | Automatic tests | ✅ 72 pass, 0 warnings (68 at the start; F-10 added 4) |
| C2 | The screens bench, one / two / three hidden screens | ✅ 43 / 43 (31 at first; it found F-9; after F-10 it resizes the leftmost screen and checks the screens touch) |
| C3 | No Sway at all | ✅ the start-up check |
| C4 | The VM ready | ✅ |
| A1–A6 | VM, one screen: starts, sizes listed, 90 % and Go Back, 80 % and Keep, the countdown undoes by itself, Quit asks | ✅ all six (Javier) |
| B1–B4 | VM, two screens: both drawn, Arrange the other way and back, one screen off and back, Identify where screens can't answer | ✅ all four (Javier) |
| C5 | 90 % on real apps | ❌ first try: *"when I try it says this screens overlap and doesn't change to 90%"* → **F-10 [#126](https://github.com/jetomev/forge-suite/issues/126)**, fixed (`57b7ac9`) → ✅ |
| C6 | 80 % on real apps | ✅ (after F-10) |
| C7 | The bar and the pop-ups at 90 % | ✅ |
| D1 | A text console, no Sway: the start-up check | ✅ |
| D2 | A text console pointed at the desktop: readable, the boxes' right edge | ✅ |
| D3 | Back to the desktop | ✅ |

## The package, installed (Javier's local tests, the same evening)

| Package | What | Result |
|---|---|---|
| 1.1.2-1 | 90 % → F9 → Esc | ❌ crash, `InvalidStateError` → **F-11 #127** → 1.1.3 |
| 1.1.3-1 | F9 pressed during the countdown | ❌ a second countdown over the first, then frozen; force-quit → **F-12 #128** → 1.1.4 |
| 1.1.4-1 | the title says 1.1.4; 90 % → F9, then F9 several times, F10, Ctrl+Q during the countdown ("Answer the countdown first"), Esc at different moments and near zero, several rounds | ✅ *"ok, all good"* → **AUR 1.1.4-1 pushed** (`41c5dc4`), the only AUR push: 1.1.1 → 1.1.4 |

## Findings

- **F-11 [#127](https://github.com/jetomev/forge-suite/issues/127)** (Javier, his local test of the **1.1.2 package**, after the run above): 90 % → F9 → Esc, and the app crashed (`InvalidStateError`) — the countdown's clock ticked once more after the answer. Screens fine. Fixed; **ships as 1.1.3** (1.1.2 was already on GitHub; it never went to the AUR).
- **F-9 [#125](https://github.com/jetomev/forge-suite/issues/125)** (Claude's bench, before the run): a screen that lists no sizes (a virtual one) crashed Settings. Fixed `43fe5a5`.
- **F-10 [#126](https://github.com/jetomev/forge-suite/issues/126)** (Javier, row C5): 80 / 90 % on a screen with a neighbour said "these screens overlap" and changed nothing — a smaller size gives a screen more desktop and it grew into the next one. Now the screens beside it slide. Fixed `57b7ac9`; the bench had missed it because it resized only the rightmost screen.

## Setup notes

- The VM's second screen: `heads='2'` on its graphics; virt-manager shows only one screen, so **virt-viewer** was installed (`nog install virt-viewer`, Javier); the VM still reported screen 2 unplugged, so it was forced on (`echo on > /sys/class/drm/card1-Virtual-2/status`) and Sway restarted.
- Never saved: every change was tried and kept or undone; no F10.
