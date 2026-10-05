# hypeForge — the fonts it needs

*Javier, 2026-10-05: "very important to document the fonts we need to bundle with the KognogOS ISO by default for the terminal apps to work properly." Terminal apps draw their icons, borders and symbols with special fonts; without them a fresh install shows empty boxes.*

Checked on the test desktop on 2026-10-05 (`fc-match` → the file → `pacman -Qo` → the package) and against KognogOS's disc list, `iso/packages.x86_64`.

| Font | Package | What needs it | On the KognogOS disc |
|---|---|---|---|
| JetBrainsMono Nerd Font | `ttf-jetbrains-mono-nerd` | **Alacritty** — so every terminal app (the Forge apps, Midnight Commander, cliamp, btop…): icons, box lines, symbols | ✅ |
| Symbols Nerd Font | `ttf-nerd-fonts-symbols` | **The top bar's icons** (Waybar): the notification bell (applet 7), and every icon added to the bar later | ❌ **missing — add it** |
| Noto Sans, Noto Sans Mono | `noto-fonts` | The everyday font (`sans-serif` / `monospace` resolve to Noto): bar text, launcher (fuzzel), lock screen (gtklock), notifications (mako) | ✅ |
| Noto Color Emoji | `noto-fonts-emoji` | Emoji in any app or notification | ✅ |
| Terminus | `terminus-font` | The text-only consoles (before any desktop starts) | ✅ |

## Rules
- **A new icon or font in any hypeForge piece means a line here**, and the package goes on the KognogOS disc list in the same step.
- Icons on the bar come from **Symbols Nerd Font** (named in `sway/waybar/style.css`), so they do not depend on which text font is installed.
- Other Nerd Fonts on the test desktop (DejaVu, Noto, Victor Mono Nerd variants) are **not needed** by hypeForge; they came with other experiments.
