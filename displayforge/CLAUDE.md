# displayForge — project rules

*Screen settings for Sway, as a Forge Suite app. Section of the Forge Suite repository (D-60); read the suite's `CLAUDE.md` too.*

- **Built on forgekit, the grubForge 2.0 / alacrittyForge look:** title bar, menu bar with underlined letters, list left, settings form right, status and hint bars; colours only through forgekit's roles; readable on a text console and at 100 columns.
- **A design is approved by Javier, screen by screen, before code is written** (`docs/design/`).
- **Never leave a screen black:** every change to a mode, position, scale or rotation is applied with a **keep-or-revert countdown** that undoes it by itself.
- **Any number of screens** (1 … 6+); never assume three.
- **Writes only user files** (`~/.config/sway/outputs`, its own settings) with a backup before every save; no password needed (ddcutil works without one here).
- **Screens that look identical to the system are told apart by the user** (Identify), and the answer is remembered — never guessed.
- Packages through nog; decisions in `docs/DECISIONS.md` (D-n); TODO.md after every step; plain words.
