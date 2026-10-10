# 03b · Colour design: why v2 looks the way it does

*Research note for the look program, 2026-10-10, written after Javier's review of the first 23 themes. It explains the design rules the second version (v2) follows, where each rule comes from, and what changed. Companion to `03-theme-system.md` (the format and the contract) and `palette/` (the generator and its output). Nothing outside `docs/research/look-2026-10/` was changed.*

## What Javier said about v1

> "More contrast. Why? that way they aren't monotone and boring (repetitive to the extreme)" · "We can use white, black, and grays inside our color themes. If not, they are extremely monotone." · "Please look for more color usage and combination, graphic designer, recommendations." · "The samples are too one sided of the color." · "add a theme with blacks, whites, dark grays, and orange combination." · "purple theme is actually our KognogOS catppuccin mocha color combinations, not purple." · "Let's use middle to darker" (for the middle themes).

**He was right, and the reason is measurable.** In v1 every surface of a theme was tinted with the theme's hue: windows, panels, bar and pop-ups were all "blue". The accent was a lighter blue. With one hue everywhere, nothing stands out. The v2 report shows it as *colour share*: of all the colour on a typical screen, how much sits on the big background areas. In v1's Blue, the windows themselves carried **56 %** of it. In v2's Blue they carry **9 %**. The colour moved to the bar, the headers and the selected row (**64 %**) and to a second, contrasting colour for small things (**28 %**).

## The rules v2 follows, and where they come from

### 1. 60 · 30 · 10: neutrals do the heavy lifting

**The rule:** about 60 % of what you see is a quiet *foundation*, 30 % is the main colour, and 10 % is a contrasting highlight. It began as an interior-design rule (walls, furniture, accessories) and is widely used in UI design for the same reason: the eye needs a calm field before a colour can stand out.

**The same idea in the design systems we learn from:**
- **Fluent 2 (Microsoft):** the system starts from a *neutral* palette ("blacks, whites, and grays that ground the interface… surfaces, text, and layout"). It warns to "avoid overusing brand colors or using them on large surfaces", and to "use shared colors sparingly to accent and highlight important areas". Semantic colours (danger, success) "carry important information, never decoration". Source: fluent2.microsoft.design/color.
- **Material 3 (Google):** every scheme has *three* accent groups (primary, secondary, tertiary), each with an "on" colour for text on it. Separately, it has *surface* roles that "don't represent your brand, but define your UI and ensure accessible color combinations". Source: Material Components docs, `docs/theming/Color.md`. Material's own site describes tertiary as the role for contrasting accents. That page renders by script and could not be read by machine today, so this sentence is from the published guidance, not quoted.
- **Apple Human Interface Guidelines:** system background colours in a neutral ladder (primary, secondary, tertiary backgrounds) with one app *accent colour* for controls and selection. Source: developer.apple.com/design/human-interface-guidelines/color.
- **Refactoring UI (Adam Wathan & Steve Schoger), chapter "Working with color":** "you need more colors than you think". In practice that means 8–10 grays, a primary with its shades, and accent colours. The grays build the interface, and colour is spent where it means something.

**How v2 applies it:** every theme has three layers.

| Layer | Share | What it is | In v2 |
|---|---|---|---|
| **Foundation** | ~60 % | windows, panels, pop-up lists, notifications, the terminal | a neutral ladder: off-white (light themes), **graphite** at OKLCH lightness ≈ 0.30 (middle themes, "middle to darker"), **charcoal** ≈ 0.185 (dark themes). At most a whisper of the hue (chroma ≤ 0.012) |
| **Band** | ~30 % | the bar, panel headers, side panels, the selected row, the focused window border | the theme's colour **at full strength**. This is where Blue is unmistakably blue |
| **Pop** | ~10 % | the letters you typed, toggles that are on, badges, buttons, links, the bell's dot | a **second colour** chosen by a harmony rule (below) |

### 2. Connected, not fused: how far apart the layers must be

hypeForge's own Phase 12 rule (D-46 area, `TODO.md`) is "contrast between elements on purpose: connected, not fused, not monotone". v2 makes it measurable:
- **band vs foundation:** at least ΔL 0.10 in lightness *and*, in coloured families, at least 0.06 more colourfulness. The bar and headers can never melt into the windows.
- **pop vs band:** at least ΔE 0.15 (a clearly different colour, not a shade of the band). This is what makes a toggle or a typed letter *pop*.
- **status vs pop:** "error" never looks like "selected" (ΔE ≥ 0.08), and the urgent border is ΔE ≥ 0.15 from the focused one.

### 3. Harmony: choosing the pop

A *harmony* is a classic way of picking colours that belong together, by their position on the colour wheel (Johannes Itten's colour theory, the basis of tools like Adobe Color).
- **Complementary:** the opposite side of the wheel. Maximum contrast, the strongest "pop".
- **Split-complementary:** the two neighbours of the opposite. Almost as strong, less harsh, and more choices when the exact opposite is a bad fit.
- **Analogous-warm:** a neighbour on the warm side. Calm, natural ("leaf and sun").

The picks, by family:

| Family | Band | Pop | Rule | Why this one |
|---|---|---|---|---|
| Blue (middle, dark) | blue | **amber** `#ffae33` | complementary | blue and amber are opposites; amber on navy is a classic high-visibility pair (signage, dashboards) |
| Light Blue | blue | **orange** `#b65400` | split-complementary | on a white window a pop must be dark enough to see, and dark amber turns muddy brown. Orange stays vivid when dark |
| Purple | violet | **mint** `#61dbac` / `#00835e` | near-complementary | violet and mint are opposite; mint stays fresh in light and dark |
| Green (middle, dark) | green | **gold** `#edb836` | analogous-warm | leaf + sun: warm, natural, and gold reads well on deep green |
| Light Green | green | **raspberry** `#c3337a` | complementary | the true opposite of green; dark gold would turn olive on white |
| Pink | pink | **teal** `#4cd9d2` / `#00817c` | complementary | pink and teal are opposites |
| Red (middle, dark) | brick / oxblood | **gold → cream** `#ffe5af`, `#ffd16b` | analogous-warm | "charcoal + cream": red on charcoal with a cream-gold highlight, warm and rich |
| Light Red | red | **deep teal** `#008085` | complementary | the opposite of red; dark gold on white would be olive |
| Grays | gray | **emblem blue** `#0363ef` (light) / `#9dc2ff` (dark) | brand | the logo's main colour on a neutral desktop, the way Windows and macOS use blue |
| Ember (new) | **emblem orange** `#d43a03` | **cream** `#f7e6c3` | warm neutral | orange blocks on black, cream highlights: Javier's "blacks, whites, dark grays and orange" |
| Multicolor | **neutral-dark** | **mauve** + eight category colours | rotation | see below |
| White, Black | gray | gray | high contrast | colour only where it means something (status, urgent, the terminal) |

**A designer's catch the generator taught us:** a pop must reach 3:1 against a white window, so in light themes it must be fairly dark. Some hues survive being dark (blue, violet, teal, raspberry, orange). Others turn muddy (amber becomes brown, gold becomes olive). So the light themes use a different harmony than their dark siblings. That is why Light Blue gets orange where Blue gets amber.

### 4. Multicolor: one neutral band, eight colours that take turns

The Multicolor themes keep the foundation **and** the band neutral (a near-black bar). The colour comes from the eight category colours (`cat.red … cat.pink`), each tuned to pass 3:1 on the window *and* on the bar:
- **each workspace number has its own colour** (1 blue, 2 purple, 3 green, 4 orange, 5 pink…), and the active one becomes a filled chip in its colour;
- the same colours mark file types in Midnight Commander, meters in the sound mixer, and series in charts;
- buttons and toggles use one pop (mauve), so controls stay predictable while the rest is playful.

A style can go further and give each workspace's focused border its own category colour. That is a style choice, written in `style.toml`, not a new theme.

### 5. KognogOS Mocha: Catppuccin's own roles

Javier: the Purple theme "is actually our KognogOS catppuccin mocha color combinations". So Mocha became its own theme, **first in the list and the default**, mapped by **Catppuccin's style guide** (github.com/catppuccin/catppuccin, `docs/style-guide.md`) with the colours from **palette.json v1.8.0** (github.com/catppuccin/palette):

| Our role | Catppuccin | The guide says |
|---|---|---|
| surface.base · sunken · bar | Base · Crust · Mantle | "Background pane: Base · Secondary panes: Crust, Mantle" |
| surface.overlay · hover | Surface 0 · Surface 1 | "Surface elements: Surface 0, 1, 2" |
| surface.raised | **#262637** | not Catppuccin: hypeForge's bar shade, kept because it is today's look |
| text.primary · secondary · muted | Text · Subtext 1 · Overlay 2 | "Body copy: Text · Sub-headlines, labels: Subtext 0/1 · Subtle: Overlay 1" (we take the brighter member, see deviations) |
| pop / accent | Mauve, text on it **Base** | Mauve is Mocha's signature; "text on accent: Base" |
| window.focused · unfocused · urgent | Lavender · Surface 1 · Yellow | "Active border: Lavender · Inactive border: Overlay 0 · Bell border: Yellow" (Overlay 0 is too close to Lavender for our focus rule, so Surface 1, today's) |
| status success · warning · danger · info | Green · Yellow · Red · Teal | "Success: Green · Warnings: Yellow · Errors: Red · Information: Teal" |
| selection | Overlay 2 at 25 % over Base = `#3b3d4f` | "Selection background: Overlay 2 at 20–30 % opacity" |
| bar.pop (the bell's dot) | Yellow | the bell border colour |
| terminal | cursor Rosewater, cursor text Crust, color0 Surface 1, color7 Subtext 0, color8 Surface 2, color15 Subtext 1, brights from palette.json | the guide's terminal table |
| cat (categories) | Red, Peach, Yellow, Green, Teal, Blue, Mauve, Pink | Mocha's accents, each with one job |

**Mocha's 60-30-10 is different, on purpose.** Its foundation keeps a blue-violet tint and its band is a stack of close panes (mantle, crust, surfaces). Its richness comes from *many* accents, each with one job: mauve for controls, lavender for the focused border, blue for links, yellow for the bell, green/yellow/red/teal for status. The design checks report this as information, not a failure.

**Deviations from Catppuccin, all listed in the report:** where no Catppuccin colour passed our rules, the generator moved lightness by the smallest step:
- `text.muted` `#9399b2` → `#959bb4`
- `pop.text` (mauve as letters) `#cba6f7` → `#d1acfe`
- `status.danger` `#f38ba8` → `#ff99b5`
- `term.red` `#f38ba8` → `#ff96b3`
- `term.blue` `#89b4fa` → `#8bb6fc`

All of them miss only APCA (the stricter perceptual score) by 0.5–5 points; WCAG already passed. Javier may prefer exact Catppuccin there. That is one line per colour.

## Before and after

| | v1 (first review) | v2 |
|---|---|---|
| Structure | every surface tinted with the theme hue; accent a lighter version of the same hue | 60 % neutral foundation · 30 % band in the theme colour · 10 % harmony pop |
| Blue (middle) | windows `#354666`, bar `#1b2d4f`, accent `#8bdeff` (all blue) | windows **graphite** `#2b2e32`, band **blue** `#0555b7`, pop **amber** `#ffae33` |
| Middle themes | lightness ≈ 0.40, tinted | "middle to darker": graphite ≈ 0.30, neutral |
| Light themes | tinted off-white, a dark accent of the same hue | off-white `#ed…`–`#f5…`, a strong mid band with white text, a contrasting pop |
| Focused border | the accent | **the band colour** as a line (`band.text`), so the focused window carries the theme colour |
| Purple | "the Kognog colours" = mauve accents on purple | real purples (band `#6e3aa8`, pop mint); **Mocha is its own theme**, the default |
| New | — | **Ember** (black, white, grays, emblem orange, cream); **KognogOS Mocha** |
| Count | 23 | 25 |
| Contract | 78 pairs per theme, 1,794 in all | 84 per theme (92 for Multicolor), **2,124 in all, all pass** |
| Colour share (Blue), same area model | foundation 56 % · bar and selection 30 % · accent 15 % | foundation 9 % · band 64 % · pop 28 % |

## What Javier is asked to look at

Open `palette/swatches.html` (one file, works offline). The strip under each name shows the 60-30-10 split, and the tiny desktop shows each layer in use. Things to judge by eye:
1. **Mocha as the default:** does it still feel like today's desktop?
2. **Ember:** the name, and whether cream is the right pop (the other candidate: a white pop with a gold hover).
3. **Light themes:** the pops are darker by necessity (orange, mint-green, raspberry, teal). Do they feel lively enough?
4. **Red's cream-gold pop:** warm and elegant, or too soft? It can move toward gold.

## Sources

- Catppuccin style guide: github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md (read 2026-10-10)
- Catppuccin palette v1.8.0: github.com/catppuccin/palette, `palette.json` (downloaded 2026-10-10 to the session scratch folder, read as data)
- Fluent 2 Color: fluent2.microsoft.design/color (read 2026-10-10)
- Material Design 3 colour roles: m3.material.io/styles/color/roles (script-rendered; roles confirmed via github.com/material-components/material-components-android `docs/theming/Color.md`)
- Apple Human Interface Guidelines, Color: developer.apple.com/design/human-interface-guidelines/color
- Adam Wathan & Steve Schoger, *Refactoring UI*, "Working with color"
- Johannes Itten, *The Art of Color* (colour harmonies)
- Colour maths and contrast: OKLab (Björn Ottosson), WCAG 2.2 (W3C), APCA-W3 0.0.98G-4g (Myndex), as in `03-theme-system.md`

Thank you to all of them. We learn from them and credit them, and we never compare.
