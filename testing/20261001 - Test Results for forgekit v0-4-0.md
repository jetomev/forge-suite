# Test Results — forgekit v0.4.0 (console mode)

*2026-10-01, desktop `tphome-linux` (KognogOS testbed), Python 3.14, Textual 8.2.8; real-console run on the `kognog-hypeforge` VM (KognogOS, kernel built-in console font).*

**Tests: 23, all passing** (v0.3.0 had none in the repo). **Warnings: 0** (`python -W default -m unittest`).

| # | Result | Notes |
|---|---|---|
| 1.1–1.2 | ✅ | |
| 2.1–2.4 | ✅ | the console font's character list was read from `default8x16`, not assumed: it lacks some Latin-1 (`Á Ó Ú À © ×`…), hence the accent fallback |
| 3.1–3.3 | ✅ | 3.3 added after the VM test (F-11) |
| 4.1–4.4 | ✅ | 4.2 guards a bug found while building: the flag first lived in `self.console`, which Textual uses for its own Rich console, so every app went into console colours |
| 5.1 | ✅ | before the change: black-on-black bars, red boxes for `╭ ╮ ╰ ╯ ▔ ▁ ▊ ▎ ⛏ —`, input frames invisible (`docs/console/v0.3.0-on-a-text-console.png`) |
| 6.1 | ✅ | identical apart from ids, all four |
| 6.2 | ✅ | |
| 7.1 | ✅ after F-11 | first run found F-11 (below); after the fix: "Dashboard" whole, tagline grey, F1 → Help works where Ctrl+H cannot. The VM was snapshotted first and reverted afterwards |
| 8.1 | ✅ | each break made the expected test fail; code restored and suite green again |

## Findings
- **F-10** — Help could not be opened from the keyboard on a text console: it sends Ctrl+H as the Backspace byte (`\x08`), which Textual reads as Backspace. **Fixed:** F1 opens Help too (the console sends `ESC [[A`, read as F1). Proven on the VM.
- **F-11** — The real console shows underline as cyan and italic as green (the emulation did not). The active menu item's underlined letter vanished on its cyan block; the About tagline turned green. **Fixed:** active item on blue, no italic in console mode; `console-preview.py` now models both and fails on any letter drawn in its own background colour.

## Not covered
- Javier's own run on the desktop's tty3 (he chose the VM instead).
- Larger console fonts (Terminus): they draw more characters, so the swap is conservative there, never wrong.
- The adopting apps (grubForge, alacrittyForge, bitlaForge, nogForge): their own fixed colours and emoji move to the roles and the glyph table when each one upgrades. Until then the kit's character swap already keeps them free of undrawable characters.
