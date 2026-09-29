#!/usr/bin/env python3
# Regenerates assets/banner.svg (README header) and assets/snap-keys.svg (the key map drawing).
# The KognogOS emblem is embedded from assets/kognogos-emblem.png, so the banner has no outside
# dependencies once generated. Run from anywhere:  python3 scripts/make-banner.py
# Check the result by rendering it:  rsvg-convert -w 1280 assets/banner.svg -o /tmp/banner.png
import base64, pathlib
root = pathlib.Path(__file__).resolve().parent.parent / "assets"
emb = base64.b64encode((root / "kognogos-emblem.png").read_bytes()).decode()
MONO = "'JetBrains Mono','DejaVu Sans Mono',Menlo,Consolas,monospace"
SANS = "Inter,'Segoe UI','DejaVu Sans',Helvetica,Arial,sans-serif"

def pill(x, y, w, label, color):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="{color}" fill-opacity=".10" stroke="{color}" stroke-opacity=".75"/>'
            f'<text x="{x + w/2}" y="{y + 23}" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="600" fill="{color}">{label}</text>')

def window(x, y, w, h, stroke, body):
    return (f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#1e1e2e" stroke="{stroke}" stroke-width="2"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="9" fill="#313244"/><rect x="{x}" y="{y+11}" width="{w}" height="9" fill="#313244"/>'
            f'<circle cx="{x+13}" cy="{y+10}" r="3.6" fill="#f38ba8"/><circle cx="{x+25}" cy="{y+10}" r="3.6" fill="#f9e2af"/><circle cx="{x+37}" cy="{y+10}" r="3.6" fill="#a6e3a1"/>'
            f'{body}</g>')

def lines(x, y, specs):
    out, yy = [], y
    for w, c in specs:
        out.append(f'<rect x="{x}" y="{yy}" width="{w}" height="7" rx="3.5" fill="{c}"/>'); yy += 16
    return "".join(out)

term = lines(806, 136, [(64,"#a6e3a1"),(128,"#cdd6f4"),(96,"#6c7086"),(140,"#89b4fa"),(72,"#cdd6f4"),(112,"#6c7086"),(56,"#cba6f7"),(120,"#cdd6f4"),(84,"#6c7086"),(30,"#a6e3a1")])
monitor = lines(1030, 146, [(60,"#94e2d5"),(132,"#45475a"),(98,"#89b4fa"),(140,"#45475a")]) + \
          '<polyline points="1030,226 1052,206 1072,216 1094,190 1116,200 1140,176 1166,186" fill="none" stroke="#fab387" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
files = "".join(f'<rect x="{1068 + (i%4)*30}" y="{244 + (i//4)*30}" width="22" height="20" rx="4" fill="{c}"/>'
                for i, c in enumerate(["#89b4fa","#f9e2af","#89b4fa","#cba6f7","#a6e3a1","#89b4fa","#fab387","#89b4fa"]))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1280 400" width="1280" height="400" role="img" aria-labelledby="t d">
<title id="t">hypeForge</title>
<desc id="d">The KognogOS Hyprland desktop: floating-first, terminal-first, one portable folder. A small drawing shows a desktop with floating windows and one window snapped to the left half with Win plus the left arrow key.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e1e2e"/><stop offset="1" stop-color="#11111b"/></linearGradient>
  <radialGradient id="glow" cx=".18" cy=".32" r=".55"><stop offset="0" stop-color="#cba6f7" stop-opacity=".16"/><stop offset="1" stop-color="#cba6f7" stop-opacity="0"/></radialGradient>
</defs>
<rect x="1" y="1" width="1278" height="398" rx="26" fill="url(#bg)" stroke="#313244" stroke-width="2"/>
<rect x="1" y="1" width="1278" height="398" rx="26" fill="url(#glow)"/>

<image x="64" y="92" width="128" height="128" xlink:href="data:image/png;base64,{emb}"/>
<text x="224" y="118" font-family="{SANS}" font-size="15" font-weight="700" letter-spacing="3" fill="#6c7086">KOGNOGOS · FORGE SUITE</text>
<text x="220" y="196" font-family="{MONO}" font-size="74" font-weight="800" letter-spacing="-2" fill="#cdd6f4">hype<tspan fill="#cba6f7">Forge</tspan></text>
<text x="224" y="240" font-family="{SANS}" font-size="22" fill="#a6adc8">The KognogOS Hyprland desktop, rebuilt light</text>
{pill(224, 272, 150, "floating-first", "#89b4fa")}
{pill(386, 272, 150, "terminal-first", "#a6e3a1")}
{pill(548, 272, 196, "one portable folder", "#fab387")}
<text x="224" y="350" font-family="{SANS}" font-size="15" fill="#6c7086">Coming soon · for any Arch install · by Javier &amp; Claude · GPLv3</text>

<rect x="776" y="56" width="440" height="286" rx="14" fill="#181825" stroke="#45475a" stroke-width="2"/>
<rect x="788" y="68" width="416" height="20" rx="7" fill="#313244"/>
<circle cx="802" cy="78" r="4" fill="#cba6f7"/><circle cx="816" cy="78" r="4" fill="#585b70"/><circle cx="830" cy="78" r="4" fill="#585b70"/>
<rect x="1150" y="74" width="42" height="8" rx="4" fill="#6c7086"/>
<rect x="788" y="98" width="204" height="234" rx="10" fill="#cba6f7" fill-opacity=".07" stroke="#cba6f7" stroke-width="2" stroke-dasharray="7 6"/>
{window(796, 106, 188, 218, "#cba6f7", term)}
{window(1014, 116, 176, 120, "#89b4fa", monitor)}
{window(1056, 226, 146, 98, "#b4befe", files)}

<g font-family="{SANS}" font-weight="700" font-size="17" fill="#cdd6f4">
  <rect x="848" y="356" width="58" height="30" rx="7" fill="#313244" stroke="#585b70"/><text x="877" y="377" text-anchor="middle">Win</text>
  <text x="920" y="377" text-anchor="middle" fill="#6c7086">+</text>
  <rect x="934" y="356" width="40" height="30" rx="7" fill="#313244" stroke="#585b70"/><text x="954" y="378" text-anchor="middle">←</text>
  <text x="990" y="377" font-weight="500" font-size="15" fill="#a6adc8">snaps it left, just like Plasma</text>
</g>
</svg>
'''
(root / "banner.svg").write_text(svg)

# --- the key map diagram: five small screens
cards = [("Win", "←", "left half",  (0, 0, .5, 1)),
         ("Win", "→", "right half", (.5, 0, .5, 1)),
         ("Win", "↑", "top half",   (0, 0, 1, .5)),
         ("Win", "↓", "bottom half",(0, .5, 1, .5)),
         ("Win", "PgUp", "maximise", (0, 0, 1, 1))]
parts = []
for i, (k1, k2, label, (fx, fy, fw, fh)) in enumerate(cards):
    x0 = 24 + i * 250; sx, sy, sw, sh = x0 + 14, 40, 208, 124
    parts.append(f'<rect x="{x0}" y="16" width="232" height="228" rx="14" fill="#181825" stroke="#313244" stroke-width="2"/>')
    parts.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8" fill="#11111b" stroke="#45475a" stroke-width="2"/>')
    parts.append(f'<rect x="{sx+6}" y="{sy+6}" width="{sw-12}" height="9" rx="4" fill="#313244"/>')
    ax, ay, aw, ah = sx + 6, sy + 21, sw - 12, sh - 27
    wx, wy, ww, wh = ax + fx*aw + 2, ay + fy*ah + 2, fw*aw - 4, fh*ah - 4
    parts.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh:.1f}" rx="5" fill="#cba6f7" fill-opacity=".22" stroke="#cba6f7" stroke-width="2"/>')
    kw2 = 34 if len(k2) == 1 else 62
    total = 50 + 16 + kw2; kx = x0 + (232 - total) / 2
    parts.append(f'<rect x="{kx:.1f}" y="180" width="50" height="28" rx="6" fill="#313244" stroke="#585b70"/><text x="{kx+25:.1f}" y="199" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="15" fill="#cdd6f4">{k1}</text>')
    parts.append(f'<text x="{kx+58:.1f}" y="199" text-anchor="middle" font-family="{SANS}" font-size="15" fill="#6c7086">+</text>')
    parts.append(f'<rect x="{kx+66:.1f}" y="180" width="{kw2}" height="28" rx="6" fill="#313244" stroke="#585b70"/><text x="{kx+66+kw2/2:.1f}" y="199" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="15" fill="#cdd6f4">{k2}</text>')
    parts.append(f'<text x="{x0+116}" y="232" text-anchor="middle" font-family="{SANS}" font-size="15" fill="#a6adc8">{label}</text>')
svg2 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1272 260" width="1272" height="260" role="img" aria-labelledby="t2">
<title id="t2">Window keys: Win plus Left or Right snaps a window to the left or right half, Win plus Up or Down to the top or bottom half, Win plus Page Up maximises.</title>
{''.join(parts)}
</svg>
'''
(root / "snap-keys.svg").write_text(svg2)
print("ok", len(svg), len(svg2))
