# 05 · Wallpapers: five per colour theme

*Research helper 5 of 5 for the look program. Date: 2026-10-10. Written by Claude for Javier.*

## The short answer

- **We can make all 115 wallpapers ourselves** (23 colour themes × 5 moods) with a small Python program. The program draws each picture from scratch using only maths, so every picture is ours, there are no licence terms to follow, and the same settings always give the same picture.
- **A working prototype exists:** `wallpapers/generate.py`. It already makes five moods (cyberpunk, buildings, nature, technology, an anime-style stand-in) for any palette. I rendered 15 samples (Purple, White/Light Gray, Dark Blue) and checked every one by eye, fixing what looked cheap.
- **The honest limit is anime.** Code can make an anime-*style* sky (flat-painted clouds, power lines, drifting petals). It cannot make real anime illustration: characters, hand-painted scenes. For that we need art made by a person, under a licence that lets us ship it.
- **Photo sites (Unsplash, Pexels) are a poor fit for shipping inside KognogOS.** Their licences are free to *use*, but they restrict selling, redistribution on "wallpaper platforms" (Pexels), or building a "similar or competing service" (Unsplash). Debian-style distributions treat these licences as not free. Wallhaven gives no licence at all. Wikimedia Commons is usable, one file at a time, when the file is public domain or Creative Commons.

**Recommendation:** use the generator for all 115 wallpapers. If Javier wants real anime art later, commission it under CC BY-SA (the licence KDE and GNOME artwork usually uses: anyone may share and change it if they credit the artist), or pick public-domain/CC0 files from Wikimedia Commons, and keep a credits file next to them.

## 1 · What code can draw well, and what it can't

"Procedural" means the picture is made by code (gradients, shapes, random numbers with a fixed seed) instead of being a photo or a painting.

| Mood | What the code draws | How good it can get | Built? |
|---|---|---|---|
| **Cyberpunk** | Synthwave: striped sun, neon perspective grid, low-poly ridges with glowing edges, stars | Very good. This style was born on computers. | ✅ `synthwave` |
| **Buildings** | City skyline in layers fading into haze, lit windows, neon signs, moon | Good. Reads as a flat illustrated city. | ✅ `skyline` |
| **Nature** | Layered mountain ranges with mist in the valleys, moon or sun, pine trees | Very good. The classic "minimal mountains" look. | ✅ `mountains` |
| **Technology** | Circuit board: routed copper lines, chips with pins, a blurred board behind for depth | Very good. | ✅ `circuit` |
| **Anime (stand-in)** | Cel-shaded cumulus towers in haze, small high clouds, moon or sun, a quiet power-line pole, a few petals | Good *as a style*. It is not anime art. | ✅ `skyclouds` |
| Nature (extra) | Aurora, ocean waves, sand dunes | Good | ⬜ ideas |
| Technology (extra) | Isometric blocks, data grids, soft bokeh light dots | Good | ⬜ ideas |
| Abstract | Geometric tiling, gradient meshes, low-poly triangles | Very good, and works for every colour | ⬜ ideas |
| Anime (real) | Characters, hand-painted streets and rooms | **Not possible with code.** Needs an artist. | — |

What makes these look finished instead of flat (all in the prototype):

- **Depth layers**: far things are lighter and closer to the sky colour, near things are darker (how real air works).
- **Haze and mist** between the layers.
- **Glow** around bright things on dark themes (sun, neon, windows, active circuit lines).
- **Fine grain** plus dithering (tiny random noise), so smooth gradients never show stripes ("banding") on a big screen.
- **A fixed seed**: the randomness is the same every run, so a theme always gets the same picture.
- **Drawn at double size, then shrunk**, so edges are smooth.

**Light themes get their own art direction.** A neon glow is invisible on white, so on light themes the same mood becomes a "paper" version: foggy daytime city, misty morning mountains, a white circuit board with soft shadows, a bright cloud sky. The White/Light Gray samples show this. They are calmer by design, because a white theme is meant to be quiet.

## 2 · The generator

File: `look-2026-10/wallpapers/generate.py`. It needs Python 3, Pillow 12.3 and numpy 2.5. Both are installed here, and nothing new was installed.

```
python3 generate.py --palette purple --motif synthwave
python3 generate.py --colors 0f1f14 1d3b26 2f7a45 74c98a b8f2c6 --mode dark --motif mountains
python3 generate.py --samples
```

- **Input:** a named palette, or any 5 or so hex colours. The program sorts the colours from background to strongest contrast and picks the most colourful one as the accent. `--mode dark|light` forces the art direction; leave it out and the program guesses from how bright the colours are. (A green test palette got guessed as "light". It still looked good, but the theme file should always say the mode.)
- **Palette roles:** `c0` background extreme · `c1`, `c2` the steps between · `accent` · `c4` strongest contrast (glow on dark, ink on light) · `hot` brightest highlight. The theme manager can feed these straight from each theme's colour file.
- **Output:** a 2560×1440 PNG, plus a 640px preview (`--preview 0` turns it off).
- **Speed:** about 5 to 8 seconds per picture on this desktop, on one core. All 115 would take roughly 12 to 15 minutes, or a few minutes if run in parallel.
- **Tested beyond the samples:** a custom green palette (mountains) and a light pink one (clouds) both came out well, so the colour-picking works for themes I didn't hand-tune.

### Size: an important finding

| Format | Purple synthwave | White mountains | Dark Blue circuit |
|---|---|---|---|
| PNG (lossless) | 4.1 MB | 3.1 MB | 4.3 MB |
| JPEG, quality 90 | 0.78 MB | 0.34 MB | 0.74 MB |
| WebP, quality 90 | 0.38 MB | 0.06 MB | 0.30 MB |

The grain that stops banding also makes PNGs big: 115 PNGs would be about **450 MB**. Two ways out:

1. **Ship the generator, not the pictures.** The theme app makes a wallpaper when a theme is chosen, in about 6 seconds, and keeps it. The package stays tiny, and any number of screens or sizes works.
2. **Ship WebP.** That's about 35 MB for all 115. swaybg (the program that shows the wallpaper in Sway) can read WebP on this desktop: the WebP image loader `libpixbufloader-webp.so` is installed. **Not yet checked:** whether WebP's compression smooths away the grain and brings banding back on the light themes. That 0.06 MB file is suspiciously small.

My pick is option 1 with a WebP cache. That's Javier's call.

**Note for the commit:** `samples/` is **58 MB** of PNGs. If this research gets committed, keep the 640px previews (about 3.5 MB) and leave the full-size PNGs out, since `--samples` re-creates them exactly.

### Three screens

Today each picture is one 2560×1440 screen. Two ways to cover three screens, neither built yet:

- **Same mood, a different seed per screen** (three related pictures): easiest, and it works for any number of screens.
- **One wide 7680×1440 picture split across the screens**: the mountains and skyline would flow across, but the code would have to handle any screen layout (hypeForge must never assume three screens).

## 3 · The samples

`look-2026-10/wallpapers/samples/`: 15 full-size PNGs plus 15 previews, and **`index.html`**, the contact sheet (open it in a browser; click a picture for full size).

| Theme | Palette used |
|---|---|
| Purple (Kognog) | `#1e1e2e` base · `#2a2442` · `#6c4fc7` · `#cba6f7` accent · `#b9a3ff` glow |
| White / Light Gray | `#ffffff` · `#eff1f5` · `#ccd0da` · `#8c8fa1` · `#4c4f69` ink |
| Dark Blue | `#0a0f1e` · `#13203d` · `#1e4fae` · `#5b9cff` · `#89b4fa` |

These are stand-in palettes. The real 23 come from helper 3's colour research and plug in unchanged.

What I fixed after looking at my own output (it took several rounds):

- **Synthwave:** the first floor came out solid white because of a perspective maths mistake. I rewrote the grid with the correct formula, so lines thin out smoothly toward the horizon without shimmering. I also added more sun stripes and a stronger sun gradient.
- **Clouds (the hardest one, about eight rounds):** early versions looked like bubble wrap, then like cut-outs with dark outlines. After the coordinator's review (the main cloud sat low-left, clipped flat, with dark blobs inside, and the picture felt lopsided), I rebuilt it as a calm anime sky:
  - three cumulus towers rise from the lower third, the tallest just left of centre to balance the pole on the right;
  - their bases dissolve into a haze bank, so nothing is clipped;
  - a row of distant clouds sits along the horizon, and four small clouds float higher up;
  - the shading now comes only from each cloud's outline, never from the puffs inside, so holes and blobs can't happen: one lit tone, one flat shadow tone on the side away from the light, a thin highlight on the edge facing it, and a scalloped flat underside;
  - the pole is slimmer and lower in contrast, with fewer wires, and there are fewer petals (none on grey themes, where they looked like dust).
- **Mountains:** I removed thin vertical streaks and a visible seam under the moon (a shading switch flipped hard at the moon's position).
- **Skyline:** each building now has its own shade, the far layer got tiny windows, and the neon became coloured, with horizontal signs.
- **Light themes:** I raised the contrast on synthwave (it was washed out) and softened the circuit chips (they were too heavy).

**Still rough (honest list):**

- The anime towers are clean but a little smooth: fewer billows inside than a painter would add, and the tallest one's crown can come out with a small overhang. It's calm, which is what was asked for; more detail inside is the next step if Javier wants it.
- Slanted skyline roofs are simple wedges. Trees are simple triangles.
- The White theme's synthwave and clouds are quiet by nature. A white theme with no colour has little to work with.
- No automatic tests yet. Every check was by eye.
- Only the 5 required moods are built. The extra ideas in the table (aurora, waves, isometric, bokeh, geometric) are not.

## 4 · Licensed images: what the terms really say

Read on 2026-10-10 from the sites themselves (quotes trimmed):

| Source | What you may do | What you may not do | Fit for shipping in KognogOS |
|---|---|---|---|
| **Unsplash License** | "download, copy, modify, distribute… for free, including for commercial purposes", no credit needed | "Images cannot be sold without significant modification." "Does not include the right to compile images from Unsplash to replicate a similar or competing service." | **Risky.** A wallpaper collection inside a theme picker is close to "a similar service". Debian-world discussions treat it as non-free. KDE has said it doesn't meet the KDE manifesto, which blocks shipping in Fedora and Debian. |
| **Pexels License** | Free to use and modify, no credit needed | "Don't redistribute or sell the photos and videos on other stock photo or **wallpaper platforms**." No unaltered resale, no implied endorsement, no use in a trademark. | **Poor.** A distribution's wallpaper set is very close to a "wallpaper platform". |
| **Wallhaven** | Nothing is granted. "All images remain property of their original owners." | Everything, unless you get permission from each owner | **No.** It's a gallery, not a licence. Much of its anime content is fan-uploaded art. |
| **Wikimedia Commons** | Depends on each file: public domain, CC0 (no conditions), CC BY (credit the author), CC BY-SA (credit, and share changes under the same licence) | Depends on the file. Some are non-free or have personality/trademark limits. | **Good, one file at a time.** Check each file's licence page, keep a credits file, and prefer CC0/public domain. |
| *Pixabay* | *Not checked in this research.* It has its own licence of the same family as Pexels. | — | *Check before using.* |

**Real anime art:** the only clean routes are (a) an artist we commission, who licenses the work CC BY-SA or grants us the right to redistribute in writing, or (b) existing CC0/CC BY-SA art from Wikimedia Commons or artists who publish that way. Fan art of real shows (characters, logos) is off the table: it belongs to the studios.

## Where this lands for the look program

- **Q-3 in `look-program.md`** ("our own generated pictures, or also licensed ones?"): this research backs **H-3**. Our generator makes all of them, and licensed art comes in only where the licence clearly allows shipping (CC0, public domain, CC BY, CC BY-SA, or a written grant), with a credits file.
- Each moment of choice is Javier's: the five moods per colour, whether to ship pictures or the generator, and whether to commission anime art.

## Commands run

```
python3 -c "import PIL; print(PIL.__version__)"   # 12.3.0
python3 -c "import numpy; print(numpy.__version__)" # 2.5.3
python3 generate.py --palette purple --motif <each>   # test rounds, into the scratchpad
python3 generate.py --samples                          # 15 samples, 103 s total
python3 generate.py --colors … --motif mountains|skyclouds   # custom green + light pink test
ls /usr/lib/gdk-pixbuf-2.0/2.10.0/loaders/             # libpixbufloader-webp.so present
which swaybg                                           # /usr/bin/swaybg
```

Nothing was installed. No system files were touched. Nothing was committed.

## Sources

- [Unsplash License](https://unsplash.com/license)
- [Pexels License](https://www.pexels.com/license/)
- [Wallhaven, About](https://wallhaven.cc/about)
- [BunsenLabs forum: packaging Unsplash wallpapers, DFSG question](https://forums.bunsenlabs.org/viewtopic.php?pid=138388)
- [Parabola issue 3109: Unsplash licence judged non-free](https://labs.parabola.nu/issues/3109)
- [KDE community list, 2019: licensing policy discussion](https://mail.kde.org/pipermail/kde-community/2019q1/005126.html)
- [Ubuntu devel IRC, 2022-12-19: Unsplash clause vs DFSG](https://irclogs.ubuntu.com/2022/12/19/%23ubuntu-devel.txt)
- [GitHub Rescator7/Hearts issue 2: KDE's position quoted](https://github.com/Rescator7/Hearts/issues/2)
