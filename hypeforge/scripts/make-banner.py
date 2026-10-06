#!/usr/bin/env python3
# Regenerates assets/banner.svg (the README header): hypeForge on Sway — the bar on top, windows
# tiled side by side. The KognogOS emblem is embedded from assets/kognogos-emblem.png, so the
# banner needs nothing from outside once generated. Run from anywhere:
#   python3 scripts/make-banner.py
# Check it by rendering:  rsvg-convert -w 1280 assets/banner.svg -o /tmp/banner.png
# Colours: Catppuccin Mocha, as in docs/THEME.md.
import base64, pathlib
root = pathlib.Path(__file__).resolve().parent.parent / "assets"
emb = base64.b64encode((root / "kognogos-emblem.png").read_bytes()).decode()
MONO = "'JetBrains Mono','DejaVu Sans Mono',Menlo,Consolas,monospace"
SANS = "Inter,'Segoe UI','DejaVu Sans',Helvetica,Arial,sans-serif"

def pill(x, y, w, label, color):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="{color}" fill-opacity=".10" stroke="{color}" stroke-opacity=".75"/>'
            f'<text x="{x + w/2}" y="{y + 23}" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="600" fill="{color}">{label}</text>')

def lines(x, y, specs, step=15):
    out, yy = [], y
    for w, c in specs:
        out.append(f'<rect x="{x}" y="{yy}" width="{w}" height="6" rx="3" fill="{c}"/>'); yy += step
    return "".join(out)

def tile(x, y, w, h, stroke, body, focused=False):
    # Sway windows: straight edges, a thin border; the focused one in the accent
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1e1e2e" stroke="{stroke}" stroke-width="{3 if focused else 1.5}"/>'
            f'{body}')

# the screen: bar on top, then three tiled windows (terminal left, two stacked right)
SX, SY, SW, SH = 800, 52, 430, 296
bar_y = SY + 10
bar = (f'<rect x="{SX+10}" y="{bar_y}" width="{SW-20}" height="22" fill="#262637"/>'
       f'<image x="{SX+14}" y="{bar_y+3}" width="16" height="16" xlink:href="data:image/png;base64,{emb}"/>'
       f'<text x="{SX+36}" y="{bar_y+15}" font-family="{SANS}" font-size="11" fill="#cdd6f4"><tspan text-decoration="underline">W</tspan>orkspaces</text>'
       f'<text x="{SX+110}" y="{bar_y+15}" font-family="{SANS}" font-size="11" fill="#cdd6f4"><tspan text-decoration="underline">F</tspan>avorites</text>'
       + "".join(f'<rect x="{SX+190+i*20}" y="{bar_y+5}" width="13" height="12" rx="2" fill="{c}"/>' for i, c in enumerate(["#cba6f7", "#89b4fa", "#a6e3a1"]))
       + "".join(f'<circle cx="{SX+290+i*15}" cy="{bar_y+11}" r="4" fill="{c}"/>' for i, c in enumerate(["#89b4fa", "#94e2d5", "#f9e2af", "#a6e3a1"]))
       + f'<text x="{SX+SW-66}" y="{bar_y+15}" font-family="{MONO}" font-size="11" fill="#cdd6f4">21:45</text>'
       f'<text x="{SX+SW-22}" y="{bar_y+15}" font-family="{SANS}" font-size="11" fill="#f38ba8">⏻</text>')
gap, top = 6, bar_y + 22 + 8
area_w, area_h = SW - 20, SY + SH - 10 - top
left_w = (area_w - gap) // 2
right_x = SX + 10 + left_w + gap
right_h = (area_h - gap) // 2
term = (f'<text x="{SX+20}" y="{top+20}" font-family="{MONO}" font-size="11" fill="#a6e3a1">❯ <tspan fill="#cdd6f4">nog update</tspan></text>'
        + lines(SX + 20, top + 32, [(150, "#6c7086"), (96, "#89b4fa"), (170, "#cdd6f4"), (60, "#6c7086"), (130, "#cba6f7"),
                                    (110, "#cdd6f4"), (84, "#6c7086"), (150, "#89b4fa"), (40, "#a6e3a1")])
        + f'<rect x="{SX+20}" y="{top+area_h-24}" width="8" height="12" fill="#cdd6f4"/>')
forge = (f'<rect x="{right_x}" y="{top}" width="{area_w-left_w-gap}" height="16" fill="#313244"/>'
         f'<text x="{right_x+8}" y="{top+12}" font-family="{MONO}" font-size="10" font-weight="700" fill="#cba6f7">displayForge</text>'
         + "".join(f'<rect x="{right_x+10+i*62}" y="{top+30}" width="54" height="34" fill="none" stroke="{c}" stroke-width="1.5"/>'
                   for i, c in enumerate(["#585b70", "#89b4fa", "#585b70"]))
         + lines(right_x + 10, top + 78, [(120, "#6c7086"), (80, "#cdd6f4")], step=12))
files = (lines(right_x + 10, top + right_h + gap + 14, [(70, "#89b4fa"), (90, "#89b4fa"), (60, "#cdd6f4"), (110, "#fab387"), (80, "#cdd6f4"), (50, "#6c7086")], step=13))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1280 400" width="1280" height="400" role="img" aria-labelledby="t d">
<title id="t">hypeForge</title>
<desc id="d">The KognogOS desktop on Sway: windows tile by themselves, terminal apps first, every setting a Forge app. A small drawing shows a screen with the hypeForge bar on top and three windows side by side: a terminal, displayForge and a file list.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e1e2e"/><stop offset="1" stop-color="#11111b"/></linearGradient>
  <radialGradient id="glow" cx=".18" cy=".32" r=".55"><stop offset="0" stop-color="#cba6f7" stop-opacity=".16"/><stop offset="1" stop-color="#cba6f7" stop-opacity="0"/></radialGradient>
</defs>
<rect x="1" y="1" width="1278" height="398" rx="26" fill="url(#bg)" stroke="#313244" stroke-width="2"/>
<rect x="1" y="1" width="1278" height="398" rx="26" fill="url(#glow)"/>

<image x="64" y="92" width="128" height="128" xlink:href="data:image/png;base64,{emb}"/>
<text x="224" y="118" font-family="{SANS}" font-size="15" font-weight="700" letter-spacing="3" fill="#6c7086">KOGNOGOS · FORGE SUITE</text>
<text x="220" y="196" font-family="{MONO}" font-size="74" font-weight="800" letter-spacing="-2" fill="#cdd6f4">hype<tspan fill="#cba6f7">Forge</tspan></text>
<text x="224" y="240" font-family="{SANS}" font-size="22" fill="#a6adc8">The KognogOS desktop on Sway, light and quick</text>
{pill(224, 272, 150, "tiles by itself", "#89b4fa")}
{pill(386, 272, 146, "terminal-first", "#a6e3a1")}
{pill(544, 272, 210, "every setting an app", "#fab387")}
<text x="224" y="350" font-family="{SANS}" font-size="15" fill="#6c7086">Building toward KognogOS 1.0 · by Javier &amp; Claude · GPLv3</text>

<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="14" fill="#11111b" stroke="#45475a" stroke-width="2"/>
{bar}
{tile(SX+10, top, left_w, area_h, "#cba6f7", term, focused=True)}
{tile(right_x, top, area_w-left_w-gap, right_h, "#585b70", forge)}
{tile(right_x, top+right_h+gap, area_w-left_w-gap, area_h-right_h-gap, "#585b70", files)}
<g font-family="{SANS}" font-weight="700" font-size="17" fill="#cdd6f4">
  <rect x="850" y="358" width="58" height="30" rx="7" fill="#313244" stroke="#585b70"/><text x="879" y="379" text-anchor="middle">Win</text>
  <text x="922" y="379" text-anchor="middle" fill="#6c7086">+</text>
  <rect x="936" y="358" width="70" height="30" rx="7" fill="#313244" stroke="#585b70"/><text x="971" y="379" text-anchor="middle">Enter</text>
  <text x="1020" y="379" font-weight="500" font-size="15" fill="#a6adc8">a terminal, tiled in</text>
</g>
</svg>
'''
(root / "banner.svg").write_text(svg)
print("banner.svg", len(svg))
