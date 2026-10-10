#!/usr/bin/env python3
"""hypeForge wallpaper generator (research prototype, 2026-10).

Draws a 2560x1440 wallpaper from a colour palette and a motif, with no
outside images: every pixel is computed here, so the output is ours and has
no licence strings attached.

    python3 generate.py --palette purple --motif synthwave
    python3 generate.py --colors 1e1e2e 2a2442 6c4fc7 cba6f7 b9a3ff --motif mountains
    python3 generate.py --samples          # the research sample set

Motifs: synthwave (cyberpunk), skyline (buildings), mountains (nature),
circuit (technology), skyclouds (anime-style stand-in).

Needs Python 3 + Pillow + numpy. Same seed in, same picture out.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

W, H = 2560, 1440
SS = 2  # supersampling factor for drawn shapes (anti-aliasing)

# ── palettes ────────────────────────────────────────────────────────────────
# Roles: c0 = the background extreme (darkest on dark themes, lightest on
# light ones), c1/c2 = steps toward the middle, accent = the most "coloured"
# colour, c4 = the strongest contrast (glow on dark themes, ink on light).
# hot (optional) = the brightest highlight; derived when missing.
PALETTES = {
    "purple": dict(mode="dark", c0="#1e1e2e", c1="#2a2442", c2="#6c4fc7",
                   accent="#cba6f7", c4="#b9a3ff", hot="#f2e9ff"),
    "white": dict(mode="light", c0="#ffffff", c1="#eff1f5", c2="#ccd0da",
                  accent="#8c8fa1", c4="#4c4f69", hot="#ffffff"),
    "darkblue": dict(mode="dark", c0="#0a0f1e", c1="#13203d", c2="#1e4fae",
                     accent="#5b9cff", c4="#89b4fa", hot="#e6f0ff"),
}


def hex2rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def lum(c):
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


class Pal:
    def __init__(self, d: dict):
        self.mode = d["mode"]
        self.dark = self.mode == "dark"
        for k in ("c0", "c1", "c2", "accent", "c4"):
            setattr(self, k, hex2rgb(d[k]))
        if "hot" in d:
            self.hot = hex2rgb(d["hot"])
        else:
            self.hot = mix(self.c4, np.ones(3, np.float32), 0.6 if self.dark else 0.0)

    @classmethod
    def from_colors(cls, colors, mode=None):
        cs = sorted((hex2rgb(c) for c in colors), key=lum)
        if mode is None:
            mode = "dark" if np.mean([lum(c) for c in cs]) < 0.45 else "light"
        if mode == "light":
            cs = cs[::-1]
        while len(cs) < 5:
            cs.insert(len(cs) // 2, mix(cs[len(cs) // 2 - 1], cs[len(cs) // 2], 0.5))
        # accent = most saturated colour that is not the background extreme
        sat = lambda c: float(c.max() - c.min())
        acc = max(cs[1:], key=sat)
        to = lambda c: "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in c)
        return cls(dict(mode=mode, c0=to(cs[0]), c1=to(cs[1]), c2=to(cs[2]),
                        accent=to(acc), c4=to(cs[-1])))


# ── small numeric helpers ───────────────────────────────────────────────────
def mix(a, b, t):
    return a + (b - a) * t


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def vgrad(stops):
    """Vertical gradient. stops = [(y_fraction, rgb), ...]."""
    ys = np.array([s[0] for s in stops], np.float32) * H
    out = np.empty((H, 3), np.float32)
    yv = np.arange(H, dtype=np.float32)
    for ch in range(3):
        out[:, ch] = np.interp(yv, ys, [s[1][ch] for s in stops])
    # smooth the joints a little
    return np.broadcast_to(out[:, None, :], (H, W, 3)).copy()


def _blur1(x, r, axis):
    pad = [(0, 0)] * x.ndim
    pad[axis] = (r + 1, r)
    xp = np.pad(x, pad, mode="edge").astype(np.float64)
    c = np.cumsum(xp, axis=axis)
    n = x.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, sigma):
    """Approximate gaussian blur (3 box passes); big sigmas run downscaled."""
    if sigma < 0.5:
        return a
    if sigma > 12:
        f = int(sigma // 6)
        h, w = a.shape[:2]
        small = resize(a, (max(1, w // f), max(1, h // f)))
        small = blur(small, sigma / f)
        return resize(small, (w, h))
    r = max(1, int(round((math.sqrt(4 * sigma * sigma + 1) - 1) / 2)))
    for _ in range(3):
        a = _blur1(a, r, 0)
        a = _blur1(a, r, 1)
    return a


def resize(a, size):
    """Resize a float array (2D or HxWx3) with bicubic filtering."""
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize(size, Image.BICUBIC))
    return np.stack([resize(a[..., i], size) for i in range(a.shape[2])], -1)


def noise2(h, w, cell, rng):
    g = rng.random((h // cell + 3, w // cell + 3)).astype(np.float32)
    big = resize(g, ((w // cell + 3) * cell, (h // cell + 3) * cell))
    return big[cell:cell + h, cell:cell + w]


def fbm2(h, w, cell, octaves, rng, gain=0.5):
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        out += amp * noise2(h, w, max(2, int(cell)), rng)
        tot += amp
        amp *= gain
        cell /= 2
    return out / tot


def noise1(n, cell, rng):
    pts = rng.random(int(n / cell) + 4).astype(np.float32)
    x = np.arange(n, dtype=np.float32) / cell
    i = np.floor(x).astype(int)
    t = x - i
    # Catmull-Rom cubic
    p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)


def fbm1(n, cell, octaves, rng, gain=0.5, ridged=False):
    out = np.zeros(n, np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        v = noise1(n, max(1.0, cell), rng)
        if ridged:
            v = 1.0 - np.abs(v * 2 - 1)
        out += amp * v
        tot += amp
        amp *= gain
        cell /= 2
    return out / tot


def over(img, alpha, color):
    """Paint `color` (rgb or HxWx3) over img with a 0..1 alpha map."""
    a = alpha[..., None]
    img *= (1 - a)
    img += a * color
    return img


def screen(img, light):
    """Additive-ish 'screen' blend for glows: never clips harshly."""
    return 1 - (1 - img) * (1 - np.clip(light, 0, 1))


def shape_mask(draw_fn, size=(W, H)):
    """Draw white shapes at SSx resolution, return an anti-aliased 0..1 mask."""
    m = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    draw_fn(ImageDraw.Draw(m), SS)
    return np.asarray(m.resize(size, Image.BOX), np.float32) / 255.0


def stars(rng, n, ymax, img_shape=(H, W), size_bias=1.0):
    """A star field: mostly tiny points, a few brighter ones with a halo."""
    field = np.zeros(img_shape, np.float32)
    ys = (rng.random(n) ** 1.3) * ymax
    xs = rng.random(n) * W
    b = rng.random(n) ** 3
    for x, y, v in zip(xs, ys, b):
        xi, yi = int(x), int(y)
        if 0 <= xi < W - 1 and 0 <= yi < H - 1:
            fx, fy = x - xi, y - yi  # bilinear splat = sub-pixel stars
            field[yi, xi] += v * (1 - fx) * (1 - fy)
            field[yi, xi + 1] += v * fx * (1 - fy)
            field[yi + 1, xi] += v * (1 - fx) * fy
            field[yi + 1, xi + 1] += v * fx * fy
    glow = blur(field, 2.5) * 6 * size_bias
    return np.clip(field * 1.6 + glow, 0, 1)


def finish(img, rng, grain=0.012):
    """Film grain + dither so gradients never band, then to 8-bit."""
    h, w = img.shape[:2]
    g = rng.normal(0, 1, (h, w)).astype(np.float32)
    g = (g * 0.7 + blur(g, 0.8) * 0.9)
    img = img + g[..., None] * grain
    dither = (rng.random((h, w, 1)) + rng.random((h, w, 1)) - 1.0) / 255.0
    img = np.clip(img + dither, 0, 1)
    return Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB")


def vignette(img, strength, color=None):
    cx, cy = W / 2, H / 2
    d = np.sqrt(((XX - cx) / (W * 0.62)) ** 2 + ((YY - cy) / (H * 0.62)) ** 2)
    v = smoothstep(0.55, 1.25, d) * strength
    if color is None:
        return img * (1 - v[..., None])
    return over(img, v, color)


# ── motif: synthwave (cyberpunk) ────────────────────────────────────────────
def m_synthwave(p: Pal, rng):
    hz = H * 0.60
    if p.dark:
        sky = vgrad([(0, p.c0 * 0.8), (0.30, p.c1), (0.52, mix(p.c1, p.c2, 0.75)),
                     (0.60, mix(p.c2, p.accent, 0.55)), (1, p.c0)])
    else:
        sky = vgrad([(0, mix(p.c2, p.c1, 0.4)), (0.35, p.c1), (0.60, p.c0), (1, p.c0)])
    img = sky
    if p.dark:
        st = stars(rng, 1400, hz * 0.95)
        st *= smoothstep(hz, hz * 0.25, YY)
        img = screen(img, st[..., None] * mix(p.c4, p.hot, 0.6))
        # faint high haze bands
        neb = fbm2(H, W, 420, 5, rng)
        neb = smoothstep(0.5, 0.85, neb) * smoothstep(hz, hz * 0.2, YY) * 0.18
        img = screen(img, neb[..., None] * p.c2)

    # the sun
    R = H * 0.27
    cx, cy = W / 2, hz - R * 0.30
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    disc = np.clip(R - d + 0.5, 0, 1)
    ty = np.clip((YY - (cy - R)) / (1.35 * R), 0, 1)
    if p.dark:
        top, midc, bot = p.hot, p.accent, mix(p.c2, p.accent, 0.15)
    else:
        top, midc, bot = p.c2, mix(p.c2, p.accent, 0.5), mix(p.accent, p.c4, 0.2)
    t2 = ty[..., None]
    suncol = np.where(t2 < 0.5, mix(top, midc, t2 * 2), mix(midc, bot, (t2 - 0.5) * 2))
    # stripes cut out of the lower half, getting thicker toward the bottom
    cut = np.ones_like(disc)
    y, k = cy - R * 0.22, 0
    while y < cy + R:
        th = 3 + k * 3.4
        band = smoothstep(y - 0.8, y + 0.8, YY) * smoothstep(y + th + 0.8, y + th - 0.8, YY)
        cut *= 1 - band
        y += th + max(9.0, 30 - k * 2.6)
        k += 1
    sun = disc * cut
    if p.dark:
        bloom = blur(disc, 70) * 0.9 + blur(disc, 220) * 0.6
        img = screen(img, bloom[..., None] * p.accent * 0.55)
    img = over(img, sun, suncol)

    # mountains on the horizon: low-poly ridges, taller toward the edges
    def ridge_layer(base, amp, n_peaks, col, edge_col, seed_off):
        xs = np.linspace(-80, W + 80, n_peaks)
        xs += rng.uniform(-40, 40, n_peaks)
        env = 0.25 + 0.75 * (np.abs(xs - W / 2) / (W / 2)) ** 1.4
        ys = base - amp * env * rng.uniform(0.35, 1.0, n_peaks)
        ys[1::2] = base - (base - ys[1::2]) * 0.45  # valleys between peaks
        pts = list(zip(xs, ys))
        poly = [(-100, hz + 2)] + pts + [(W + 100, hz + 2)]
        m = shape_mask(lambda dr, s: dr.polygon([(x * s, y * s) for x, y in poly], fill=255))
        m *= YY <= hz + 2
        # facet shading: a vertical gradient inside the ridge
        shade = smoothstep(hz, base - amp, YY)[..., None]
        fill = mix(col, edge_col, shade * 0.35)
        out = over(img, m, fill)
        # glowing ridge line
        line = shape_mask(lambda dr, s: dr.line([(x * s, y * s) for x, y in pts],
                                                fill=255, width=int(2.2 * s), joint="curve"))
        line *= YY <= hz
        return out, line

    if p.dark:
        img, l1 = ridge_layer(hz, H * 0.20, 19, mix(p.c1, p.c2, 0.35), p.accent, 1)
        img = screen(img, (l1 * 0.55 + blur(l1, 6) * 0.9)[..., None] * p.accent * 0.7)
        img, l2 = ridge_layer(hz, H * 0.11, 27, p.c1 * 0.85, p.c2, 2)
        img = screen(img, (l2 * 0.8 + blur(l2, 5) * 1.1)[..., None] * p.c4)
    else:
        img, _ = ridge_layer(hz, H * 0.20, 19, mix(p.c2, p.accent, 0.25), p.c0, 1)
        img, l2 = ridge_layer(hz, H * 0.11, 27, mix(p.accent, p.c4, 0.2), p.c1, 2)
        img = over(img, l2 * 0.6, p.c0)

    # the floor with a perspective grid, computed per pixel
    dy = np.maximum(YY - hz, 0.5)
    floor = YY > hz
    if p.dark:
        fcol = vgrad([(0, p.c0), (hz / H, mix(p.c1, p.c2, 0.5)), (0.75, p.c0 * 0.9), (1, p.c0 * 0.6)])
    else:
        fcol = vgrad([(0, p.c0), (hz / H, p.c1), (1, p.c0)])
    img = np.where(floor[..., None], fcol, img)
    # camera over an endless floor: row depth = C / dy, world x = S * dx / dy
    C, S = 2765.0, 5.0
    zoff = rng.random()
    gz = C / dy + zoff                           # world z, one line per unit
    gx = S * (XX - W / 2) / dy                   # world x, one line per unit
    dgz = C / dy ** 2                            # world units per pixel (rows)
    dgx = S / dy                                 # world units per pixel (cols)

    def lines(g, dg, width):
        px = np.abs(g - np.round(g)) / dg        # pixel distance to nearest line
        wpx = width / dg                         # true line width in pixels
        cov = np.clip(wpx / 1.2, 0, 1)           # thinner than a pixel -> dimmer
        return np.clip(np.maximum(wpx, 1.2) / 2 - px + 0.5, 0, 1) * cov
    gl = np.maximum(lines(gz, dgz, 0.035), lines(gx, dgx, 0.030))
    # fade where the lines get denser than a few pixels (no moire)
    gl *= smoothstep(1.0, 6.0, 1.0 / dgz) * 0.6 + 0.4 * smoothstep(1.5, 8.0, 1.0 / dgz)
    fade = smoothstep(hz + 1, hz + 70, YY)       # avoid moire at the horizon
    gl = gl * fade * floor
    if p.dark:
        gcol = mix(p.accent, p.c4, 0.4)
        glow = blur(gl, 3.5) * 1.6 + blur(gl, 14) * 0.9
        img = screen(img, (gl * 0.85)[..., None] * gcol + glow[..., None] * p.c2 * 0.9)
        # sun reflection on the floor
        refl = np.exp(-((XX - cx) / (R * 0.55)) ** 2) * np.exp(-(YY - hz) / 160) * floor
        img = screen(img, (refl * 0.30)[..., None] * p.accent)
        # horizon fog glow
        fog = np.exp(-((YY - hz) / 26) ** 2) * 0.55 + np.exp(-((YY - hz) / 110) ** 2) * 0.25
        img = screen(img, fog[..., None] * mix(p.c2, p.accent, 0.6))
        img = vignette(img, 0.55)
    else:
        img = over(img, np.clip(gl * 0.9, 0, 1), mix(p.accent, p.c4, 0.45))
        fog = np.exp(-((YY - hz) / 30) ** 2) * 0.6 + np.exp(-((YY - hz) / 120) ** 2) * 0.25
        img = over(img, np.clip(fog, 0, 1), p.c0)
        img = vignette(img, 0.10, p.c2)
    return img


# ── motif: skyline (buildings) ──────────────────────────────────────────────
def m_skyline(p: Pal, rng):
    if p.dark:
        horizon_col = mix(p.c2, p.accent, 0.35)
        img = vgrad([(0, p.c0 * 0.75), (0.45, p.c1), (0.85, mix(p.c1, horizon_col, 0.7)), (1, horizon_col)])
        st = stars(rng, 700, H * 0.55) * smoothstep(H * 0.6, H * 0.1, YY) * 0.7
        img = screen(img, st[..., None] * p.c4)
        # big soft moon halo
        mx, my, mr = W * 0.73, H * 0.24, 70
        d = np.sqrt((XX - mx) ** 2 + (YY - my) ** 2)
        moon = np.clip(mr - d + 0.5, 0, 1)
        img = screen(img, (blur(moon, 90) * 0.7 + blur(moon, 300) * 0.5)[..., None] * p.c2 * 0.8)
        crater = fbm2(H, W, 40, 3, rng)
        img = over(img, moon, mix(p.hot, p.c4, 0.35 + 0.25 * crater[..., None]))
        clouds = smoothstep(0.52, 0.8, fbm2(H, W, 600, 5, rng)) * smoothstep(H * 0.7, H * 0.2, YY)
        img = over(img, clouds * 0.25, mix(p.c1, p.c2, 0.3))
    else:
        horizon_col = p.c0
        img = vgrad([(0, mix(p.c2, p.c1, 0.35)), (0.55, p.c1), (1, p.c0)])
        mx, my, mr = W * 0.73, H * 0.26, 90
        d = np.sqrt((XX - mx) ** 2 + (YY - my) ** 2)
        sun = np.clip(mr - d + 0.5, 0, 1)
        img = screen(img, blur(sun, 160)[..., None] * 0.5 * np.ones(3))
        img = over(img, sun, p.c0)
        clouds = smoothstep(0.5, 0.8, fbm2(H, W, 600, 5, rng)) * smoothstep(H * 0.7, H * 0.15, YY)
        img = over(img, clouds * 0.45, p.c0)

    # layers far -> near: (min h, max h, min w, max w, window size, colour t)
    layers = [
        (0.30, 0.62, 40, 110, 3, 0.18),
        (0.22, 0.52, 60, 150, 5, 0.42),
        (0.14, 0.45, 90, 200, 7, 0.70),
        (0.06, 0.30, 140, 300, 9, 1.00),
    ]
    near_col = p.c0 * 0.55 if p.dark else mix(p.c2, p.c4, 0.55)
    for li, (hmin, hmax, wmin, wmax, wsz, t) in enumerate(layers):
        col = mix(horizon_col if p.dark else mix(p.c1, p.c2, 0.6), near_col, t)
        if p.dark and li == 0:
            col = mix(p.c1, p.c2, 0.45)
        rects, extras = [], []
        x = -rng.uniform(0, wmax)
        while x < W:
            bw = rng.uniform(wmin, wmax)
            bh = H * rng.uniform(hmin, hmax) * (0.75 + 0.5 * rng.random() ** 2)
            top = H - bh
            rects.append((x, top, x + bw, H))
            r = rng.random()
            if r < 0.35:  # setback tower
                sw = bw * rng.uniform(0.45, 0.75)
                sx = x + (bw - sw) * rng.random()
                sh = bh * rng.uniform(0.08, 0.22)
                extras.append(("rect", (sx, top - sh, sx + sw, top + 1)))
                if rng.random() < 0.5:
                    ax = sx + sw / 2
                    extras.append(("ant", (ax, top - sh - bh * rng.uniform(0.05, 0.15), ax, top - sh)))
            elif r < 0.5:  # slanted roof
                extras.append(("poly", [(x, top + 1), (x + bw, top + 1),
                                        (x + bw, top - bw * 0.35) if rng.random() < .5 else (x, top - bw * 0.35)]))
            elif r < 0.62:
                ax = x + bw * rng.uniform(0.2, 0.8)
                extras.append(("ant", (ax, top - bh * rng.uniform(0.04, 0.12), ax, top)))
            x += bw + (rng.uniform(-wmin * 0.4, wmin * 0.25))

        def draw(dr, s, rects=rects, extras=extras, li=li):
            for r_ in rects:
                dr.rectangle([v * s for v in r_], fill=255)
            for kind, geo in extras:
                if kind == "rect":
                    dr.rectangle([v * s for v in geo], fill=255)
                elif kind == "poly":
                    dr.polygon([(a * s, b * s) for a, b in geo], fill=255)
                else:
                    dr.line([v * s for v in geo], fill=255, width=int((2 + li) * s))
        m = shape_mask(draw)
        tones_ = [rng.uniform(-1, 1) for _ in rects]
        tm = shape_mask(lambda dr, s: [dr.rectangle([v * s for v in r_], fill=int(128 + 100 * tv))
                                       for r_, tv in zip(rects, tones_)])
        tone = np.where(m > 0.02, tm / np.maximum(m, 1e-3), 0.5) * 2 - 1  # -1..1 per building
        vary = (1 + 0.07 * tone * (0.4 + 0.6 * t))[..., None]
        # each layer is a touch lighter toward the street (city glow in the fog)
        lift = (smoothstep(H * 0.4, H, YY) * (0.10 if p.dark else 0.0))[..., None]
        fill = col * vary
        fill = mix(fill, horizon_col if p.dark else p.c0, lift)
        img = over(img, m, fill)

        # windows
        if wsz:
            emis = np.zeros((H, W, 3), np.float32)
            wm = Image.new("RGB", (W, H), (0, 0, 0))
            wd = ImageDraw.Draw(wm)
            for (x0, y0, x1, y1) in rects:
                gap = wsz * 1.9
                cols = int((x1 - x0 - wsz) // gap)
                rows = int((y1 - y0 - wsz * 2) // (wsz * 2.2))
                if cols < 1 or rows < 1:
                    continue
                ox = x0 + (x1 - x0 - cols * gap) / 2 + wsz * 0.45
                density = rng.uniform(0.08, 0.45) if p.dark else rng.uniform(0.15, 0.4)
                tint = rng.random()
                for rr in range(rows):
                    floor_on = rng.random() < 0.85
                    for cc in range(cols):
                        if not floor_on or rng.random() > density:
                            continue
                        if p.dark:
                            c = p.hot if tint < 0.25 else (p.c4 if tint < 0.75 else p.accent)
                            if rng.random() < 0.08:
                                c = p.accent
                            v = rng.uniform(0.45, 1.0) * (0.55 + 0.45 * t)
                        else:
                            c = p.c0 if rng.random() < 0.6 else p.c4
                            v = rng.uniform(0.25, 0.6)
                        wx = ox + cc * gap
                        wy = y0 + wsz * 1.5 + rr * wsz * 2.2
                        wd.rectangle([wx, wy, wx + wsz - 1, wy + wsz * 1.2 - 1],
                                     fill=tuple(int(255 * v * ci) for ci in c))
            emis = np.asarray(wm, np.float32) / 255.0
            emis *= m[..., None] > 0.5
            if p.dark:
                img = screen(img, emis + blur(emis, 4) * 1.3 + blur(emis, 18) * 0.5)
            else:
                a = emis.max(-1)
                img = over(img, np.clip(a * 1.6, 0, 1) * 0.5, emis / np.maximum(a[..., None], 1e-3))

        # haze in front of this layer (fog rises from the street)
        if li < len(layers) - 1:
            fogy = H * (1.0 - 0.10 - 0.05 * li)
            fog = smoothstep(fogy - H * 0.30, H, YY) * (0.55 - li * 0.1)
            img = over(img, fog, horizon_col if p.dark else p.c0)

    if p.dark:
        # neon signs on the nearest layer: vertical bars with bloom
        neon = shape_mask(lambda dr, s: [dr.rounded_rectangle(
            [(x := rng.uniform(80, W - 80)) * s, (y := rng.uniform(H * 0.74, H * 0.88)) * s,
             (x + rng.uniform(6, 10)) * s, (y + rng.uniform(60, 150)) * s], radius=3 * s, fill=255)
            for _ in range(9)])
        neon2 = shape_mask(lambda dr, s: [dr.rounded_rectangle(
            [(x := rng.uniform(80, W - 200)) * s, (y := rng.uniform(H * 0.70, H * 0.86)) * s,
             (x + rng.uniform(70, 160)) * s, (y + 7) * s], radius=3 * s, fill=255)
            for _ in range(4)])
        neon = np.maximum(neon, neon2)
        ncol = mix(p.accent, p.hot, 0.45)
        img = screen(img, (neon * 0.95)[..., None] * ncol
                     + (blur(neon, 6) * 1.4 + blur(neon, 30) * 0.9)[..., None] * mix(p.accent, p.c2, 0.3))
        street = np.exp(-((H - YY) / 60) ** 2) * 0.35
        img = screen(img, street[..., None] * p.accent)
        img = vignette(img, 0.45)
    else:
        img = vignette(img, 0.12, p.c2)
    return img


# ── motif: mountains (nature) ───────────────────────────────────────────────
def m_mountains(p: Pal, rng):
    sx, sy = W * 0.36, H * 0.34
    if p.dark:
        haze = mix(p.c2, p.accent, 0.30)
        img = vgrad([(0, p.c0 * 0.8), (0.35, p.c1), (0.62, mix(p.c1, haze, 0.75)), (1, haze)])
        st = stars(rng, 1600, H * 0.6) * smoothstep(H * 0.62, H * 0.05, YY)
        img = screen(img, st[..., None] * mix(p.c4, p.hot, 0.5))
        # moon with a wide halo
        d = np.sqrt((XX - sx) ** 2 + (YY - sy) ** 2)
        moon = np.clip(58 - d + 0.5, 0, 1)
        img = screen(img, (blur(moon, 60) * 0.9 + blur(moon, 260) * 0.8)[..., None] * p.accent * 0.6)
        img = over(img, moon, p.hot)
        far_col, near_col = mix(p.c1, haze, 0.55), p.c0 * 0.55
    else:
        haze = p.c0
        img = vgrad([(0, mix(p.c2, p.c1, 0.3)), (0.5, p.c1), (1, p.c0)])
        d = np.sqrt((XX - sx) ** 2 + (YY - sy) ** 2)
        sun = np.clip(80 - d + 0.5, 0, 1)
        img = screen(img, (blur(sun, 120) * 0.6)[..., None] * np.ones(3))
        img = over(img, sun, np.ones(3, np.float32))
        far_col, near_col = mix(p.c1, p.c2, 0.6), mix(p.c2, p.c4, 0.75)

    n = 7
    for i in range(n):
        t = i / (n - 1)
        base = H * (0.50 + 0.36 * t ** 1.15)
        amp = H * (0.20 - 0.10 * t)
        prof = fbm1(W, W * (0.35 - 0.18 * t), 6, rng, gain=0.52, ridged=(i < 4))
        prof = (prof - prof.min()) / (prof.max() - prof.min() + 1e-6)
        ridge = base - amp * prof
        col = mix(far_col, near_col, t ** 0.85)
        inside = YY >= ridge[None, :]
        a = np.clip(YY - ridge[None, :] + 0.5, 0, 1)
        # light side: slopes facing the moon/sun are a bit lighter near the crest
        sm_r = ridge
        for _ in range(3):
            sm_r = _blur1(sm_r, 14, 0)
        slope = np.gradient(sm_r)
        # smooth turn-over under the moon/sun (a hard sign flip makes a seam)
        facing = np.clip(-slope * np.tanh((sx - XX[0]) / 400.0) * 0.9, -1, 1)
        depth = np.exp(-(YY - ridge[None, :]) / (60 + 80 * t)) * inside
        lit = facing[None, :] * depth * (0.10 if p.dark else 0.08)
        fill = col[None, None, :] * (1 + lit[..., None]) if p.dark else \
            mix(col, p.c0, np.clip(lit, 0, 1)[..., None] * 2.2)
        img = over(img, a, fill)
        # mist pooling in the valleys in front of this ridge
        if i < n - 1:
            top = base - amp * 0.35
            mist = smoothstep(top, base + H * 0.07, YY) * (0.62 - 0.05 * i)
            wisp = 0.75 + 0.25 * fbm2(H, W, 300, 3, rng)
            img = over(img, mist * wisp, haze)

        if i == n - 1:  # pine trees along the nearest ridge
            def trees(dr, s, ridge=ridge):
                x = 0
                while x < W:
                    th = rng.uniform(30, 95)
                    tw = th * rng.uniform(0.28, 0.38)
                    yb = ridge[int(min(W - 1, x))] + 6
                    for k in range(4):  # stacked tiers
                        f = k / 4
                        y_top = yb - th * (1 - f * 0.8) - th * 0.15
                        w_ = tw * (0.5 + 0.5 * (1 - f) ** 0.5) * (1 - f * 0.25)
                        dr.polygon([(x * s, (y_top) * s), ((x - w_) * s, (yb - th * f * 0.55) * s),
                                    ((x + w_) * s, (yb - th * f * 0.55) * s)], fill=255)
                    dr.rectangle([(x - 2) * s, (yb - 8) * s, (x + 2) * s, (yb + 20) * s], fill=255)
                    x += rng.uniform(12, 60) if rng.random() < 0.75 else rng.uniform(80, 260)
            tm = shape_mask(trees)
            img = over(img, tm, col * 0.85 if p.dark else mix(col, p.c4, 0.3))
    if p.dark:
        img = vignette(img, 0.45)
    else:
        img = vignette(img, 0.10, p.c2)
    return img


# ── motif: circuit (technology) ─────────────────────────────────────────────
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def _route(rng, cell, gw, gh, occ, n_traces, chips):
    """Random-walk traces on a grid: 45-degree turns only, no crossings."""
    traces = []
    starts = []
    for (cx0, cy0, cx1, cy1) in chips:  # pins on the chip edges
        for gx in range(cx0, cx1 + 1, 1):
            starts.append(((gx, cy0 - 1), 6))
            starts.append(((gx, cy1 + 1), 2))
        for gy in range(cy0, cy1 + 1, 1):
            starts.append(((cx0 - 1, gy), 4))
            starts.append(((cx1 + 1, gy), 0))
    rng.shuffle(starts)
    for _ in range(n_traces):
        starts.append(((int(rng.integers(0, gw)), int(rng.integers(0, gh))), int(rng.integers(0, 8)) & ~1))
    for (gx, gy), d in starts:
        if not (0 <= gx < gw and 0 <= gy < gh) or occ[gy, gx]:
            continue
        path = [(gx, gy)]
        occ[gy, gx] = 1
        L = int(rng.integers(6, 46))
        straight = 0
        for _ in range(L):
            choices = [d]
            if straight > 2 and rng.random() < 0.28:
                choices = [(d + 1) % 8, (d - 1) % 8]
            moved = False
            for nd in sorted(choices, key=lambda _: rng.random()) + [d]:
                dx, dy = DIRS[nd]
                nx, ny = path[-1][0] + dx, path[-1][1] + dy
                if 0 <= nx < gw and 0 <= ny < gh and not occ[ny, nx]:
                    # diagonal moves must not cut through a diagonal neighbour pair
                    if dx and dy and occ[path[-1][1], nx] and occ[ny, path[-1][0]]:
                        continue
                    straight = straight + 1 if nd == d else 0
                    d = nd
                    path.append((nx, ny))
                    occ[ny, nx] = 1
                    moved = True
                    break
            if not moved:
                break
        if len(path) >= 4:
            traces.append(path)
        elif len(path) > 0:
            for (x, y) in path:
                occ[y, x] = 0
    return traces


def _circuit_layer(p, rng, scale, n_chips, active_frac):
    cell = int(30 * scale)
    gw, gh = W // cell + 2, H // cell + 2
    occ = np.zeros((gh, gw), np.uint8)
    chips = []
    for _ in range(n_chips * 6):
        if len(chips) >= n_chips:
            break
        cw, ch = int(rng.integers(3, 9)), int(rng.integers(3, 7))
        x0, y0 = int(rng.integers(2, gw - cw - 2)), int(rng.integers(2, gh - ch - 2))
        if occ[y0 - 2:y0 + ch + 3, x0 - 2:x0 + cw + 3].any():
            continue
        occ[y0 - 1:y0 + ch + 2, x0 - 1:x0 + cw + 2] = 1
        chips.append((x0, y0, x0 + cw, y0 + ch))
    # free the pin rings so traces can start there
    for (x0, y0, x1, y1) in chips:
        occ[y0 - 1, x0:x1 + 1] = 0
        occ[y1 + 1, x0:x1 + 1] = 0
        occ[y0:y1 + 1, x0 - 1] = 0
        occ[y0:y1 + 1, x1 + 1] = 0
    traces = _route(rng, cell, gw, gh, occ, int(gw * gh * 0.06), chips)
    off = -cell / 2
    P = lambda g: (g[0] * cell + off, g[1] * cell + off)
    active = [rng.random() < active_frac for _ in traces]
    lw = max(2.0, 4.2 * scale)

    def draw_traces(sel):
        def fn(dr, s):
            for tr, a in zip(traces, active):
                if a != sel:
                    continue
                pts = [(P(g)[0] * s, P(g)[1] * s) for g in tr]
                dr.line(pts, fill=255, width=int(lw * s), joint="curve")
                for end in (pts[0], pts[-1]):
                    r = lw * 1.7 * s
                    dr.ellipse([end[0] - r, end[1] - r, end[0] + r, end[1] + r], fill=255)
        return shape_mask(fn)

    def draw_holes(sel):
        def fn(dr, s):
            for tr, a in zip(traces, active):
                if a != sel:
                    continue
                for g in (tr[0], tr[-1]):
                    x, y = P(g)
                    r = lw * 0.75 * s
                    dr.ellipse([x * s - r, y * s - r, x * s + r, y * s + r], fill=255)
        return shape_mask(fn)

    def draw_chips(dr, s):
        for (x0, y0, x1, y1) in chips:
            a, b = P((x0, y0)), P((x1, y1))
            dr.rounded_rectangle([(a[0] - cell * 0.35) * s, (a[1] - cell * 0.35) * s,
                                  (b[0] + cell * 0.35) * s, (b[1] + cell * 0.35) * s],
                                 radius=int(cell * 0.25 * s), fill=255)

    def draw_pins(dr, s):
        for (x0, y0, x1, y1) in chips:
            for gx in range(x0, x1 + 1):
                for gy in (y0 - 0.62, y1 + 0.62):
                    x, y = P((gx, gy))
                    dr.rectangle([(x - lw) * s, (y - cell * 0.18) * s, (x + lw) * s, (y + cell * 0.18) * s], fill=255)
            for gy in range(y0, y1 + 1):
                for gx in (x0 - 0.62, x1 + 0.62):
                    x, y = P((gx, gy))
                    dr.rectangle([(x - cell * 0.18) * s, (y - lw) * s, (x + cell * 0.18) * s, (y + lw) * s], fill=255)

    # pulses: bright dots partway along active traces
    pulses = []
    for tr, a in zip(traces, active):
        if a and rng.random() < 0.7:
            k = int(rng.integers(1, len(tr) - 1))
            pulses.append(P(tr[k]))
    pm = shape_mask(lambda dr, s: [dr.ellipse([(x - lw * 1.4) * s, (y - lw * 1.4) * s,
                                                (x + lw * 1.4) * s, (y + lw * 1.4) * s], fill=255)
                                   for x, y in pulses])
    return dict(dim=draw_traces(False), act=draw_traces(True), hdim=draw_holes(False),
                hact=draw_holes(True), chips=shape_mask(draw_chips), pins=shape_mask(draw_pins),
                pulses=pm, cell=cell)


def m_circuit(p: Pal, rng):
    if p.dark:
        base = mix(p.c0, p.c1, 0.35)
        img = np.broadcast_to(base, (H, W, 3)).copy()
        tex = fbm2(H, W, 500, 5, rng)
        img = screen(img, (smoothstep(0.35, 0.9, tex) * 0.10)[..., None] * p.c2)
        # a soft key light from the upper left
        key = np.exp(-(((XX - W * 0.3) / (W * 0.55)) ** 2 + ((YY - H * 0.3) / (H * 0.7)) ** 2))
        img = screen(img, (key * 0.16)[..., None] * p.c2)
    else:
        img = vgrad([(0, p.c0), (1, p.c1)])
        tex = fbm2(H, W, 500, 5, rng)
        img = over(img, smoothstep(0.4, 0.9, tex) * 0.25, p.c1)

    # far layer: big, blurred, dim = depth
    far = _circuit_layer(p, rng, 2.4, 4, 0.25)
    fcol = mix(p.c1, p.c2, 0.55) if p.dark else mix(p.c1, p.c2, 0.6)
    farmask = blur(np.maximum(far["dim"], far["act"]), 5)
    img = over(img, farmask * (0.55 if p.dark else 0.6), fcol)
    img = over(img, blur(far["chips"], 6) * 0.5, p.c1 if p.dark else p.c2)
    if p.dark:
        img = screen(img, blur(far["act"], 12)[..., None] * p.c2 * 0.5)

    near = _circuit_layer(p, rng, 1.0, 9, 0.16)
    if p.dark:
        dim_col = mix(p.c1, p.c2, 0.45)
        act_col = mix(p.accent, p.hot, 0.2)
        # drop shadow under copper
        sh = blur(np.maximum(near["dim"], near["act"]), 3)
        img = over(img, np.roll(sh, (4, 3), (0, 1)) * 0.45, p.c0 * 0.5)
        img = over(img, near["dim"], dim_col)
        img = over(img, near["hdim"], p.c0)
        # chips
        img = over(img, np.roll(blur(near["chips"], 8), (8, 6), (0, 1)) * 0.6, p.c0 * 0.4)
        img = over(img, near["pins"], mix(p.c2, p.c4, 0.4))
        cg = (np.clip(YY / H, 0, 1))[..., None]
        img = over(img, near["chips"], mix(p.c0 * 0.9, p.c1 * 0.8, 1 - cg))
        edge = np.clip(near["chips"] - np.roll(near["chips"], (2, 2), (0, 1)), 0, 1)
        img = screen(img, (edge * 0.5)[..., None] * p.c2)
        # active traces glow
        a = near["act"]
        img = over(img, a, act_col * 0.85)
        img = screen(img, (blur(a, 4) * 0.9 + blur(a, 22) * 0.7)[..., None] * p.accent * 0.75)
        img = over(img, near["hact"], p.c0)
        pm = near["pulses"]
        img = screen(img, (pm + blur(pm, 5) * 2.0 + blur(pm, 25) * 1.0)[..., None] * p.hot)
        img = vignette(img, 0.6)
    else:
        dim_col = mix(p.c2, p.accent, 0.35)
        act_col = mix(p.accent, p.c4, 0.55)
        sh = blur(np.maximum(near["dim"], near["act"]), 4)
        img = over(img, np.roll(sh, (5, 4), (0, 1)) * 0.22, p.c4)
        img = over(img, near["dim"], dim_col)
        img = over(img, near["hdim"], p.c0)
        img = over(img, np.roll(blur(near["chips"], 10), (10, 8), (0, 1)) * 0.30, p.c4)
        img = over(img, near["pins"], p.accent)
        img = over(img, near["chips"], mix(p.accent, p.c4, 0.5))
        edge = np.clip(np.roll(near["chips"], (-2, -2), (0, 1)) * 0 + near["chips"] - np.roll(near["chips"], (2, 2), (0, 1)), 0, 1)
        img = over(img, edge * 0.35, p.c0)
        img = over(img, near["act"], act_col)
        img = over(img, near["hact"], p.c0)
        img = vignette(img, 0.12, p.c2)
    return img


# ── motif: sky-clouds (anime-style stand-in) ────────────────────────────────
def _cumulus_puffs(rng, cx, base, width, height, scale, lean=0.0):
    """Puffs for one cloud: a broad base narrowing into a rounded tower."""
    puffs = []
    levels = max(3, int(height / (85 * scale)))
    for li in range(levels):
        f = li / (levels - 1)                      # 0 = bottom, 1 = top
        w = width * (1 - 0.74 * f ** 0.85) * rng.uniform(0.85, 1.08)
        xc = cx + lean * f * width * 0.18 + rng.normal(0, width * 0.05)
        n = max(2, int(round(w / (95 * scale))))
        for k in range(n):
            u = (k + 0.5) / n * 2 - 1
            r = (w / n) * rng.uniform(0.55, 0.95) + 18 * scale
            r *= 1.0 + 0.35 * abs(u) * rng.uniform(0.5, 1.2)  # bulging shoulders
            y = base - f * (height - r) - r * 0.35 + rng.normal(0, 10 * scale)
            puffs.append((xc + u * (w / 2 - r * 0.45), y, r, f < 0.22 and levels >= 5))
    # a rounded crown
    top_w = width * 0.30
    for _ in range(4):
        r = top_w * rng.uniform(0.26, 0.40)
        puffs.append((cx + lean * width * 0.18 + rng.uniform(-0.3, 0.3) * top_w,
                      base - height + r * rng.uniform(0.95, 1.15), r, False))
    return puffs


def _paint_cloud(img, puffs, base, height, scale, lit, shade, haze, L3, th=0.56, rng=None, hi=None):
    """Cel-shaded cloud from puffs: two flat tones, no blobs.

    The puffs make the outline. The shading is worked out from the outline
    only (never from the puffs inside), so the body is one clean lit tone,
    the side away from the light gets one flat shadow tone that follows the
    scallops, the edge facing the light gets a thin highlight, and the
    bottom row of puffs on big clouds is the flat shadowed underside.
    Rendered at 2x and scaled down for clean edges.
    """
    pad = 4
    x0 = int(max(0, min(c[0] - c[2] for c in puffs) - pad))
    x1 = int(min(W, max(c[0] + c[2] for c in puffs) + pad))
    y0 = int(max(0, min(c[1] - c[2] for c in puffs) - pad))
    y1 = int(min(H, max(c[1] + c[2] for c in puffs) + pad))
    if x1 - x0 < 8 or y1 - y0 < 8:
        return img
    S2 = 2
    pw, ph = (x1 - x0) * S2, (y1 - y0) * S2
    zb = np.full((ph, pw), -1e9, np.float32)
    dotm = np.zeros((ph, pw), np.float32)
    gy_, gx_ = np.mgrid[0:ph, 0:pw].astype(np.float32)
    gy_ = gy_ / S2 + y0
    gx_ = gx_ / S2 + x0
    lx, ly, lz = L3
    under = np.zeros((ph, pw), bool)
    for (x, y, r, low) in puffs:
        bx0, bx1 = int(max(0, (x - r - x0) * S2)), int(min(pw, (x + r - x0) * S2 + 2))
        by0, by1 = int(max(0, (y - r - y0) * S2)), int(min(ph, (y + r - y0) * S2 + 2))
        if bx1 <= bx0 or by1 <= by0:
            continue
        dx = gx_[by0:by1, bx0:bx1] - x
        dy = gy_[by0:by1, bx0:bx1] - y
        h2 = r * r - dx * dx - dy * dy
        hz_ = np.sqrt(np.maximum(h2, 0))
        z = hz_ + (y - base) * 0.6 + (0 if low else 0)  # lower puffs sit in front
        win = (h2 > 0) & (z > zb[by0:by1, bx0:bx1])
        zb[by0:by1, bx0:bx1][win] = z[win]
        d = (dx * lx + dy * ly + hz_ * lz) / r
        dotm[by0:by1, bx0:bx1][win] = d[win]
        under[by0:by1, bx0:bx1][win] = low
    M = (zb > -1e8).astype(np.float32)
    # the underside: the bottom row of puffs is all shade, so its top edge is
    # scalloped like the puffs themselves
    # shading comes from the outline only (a soft dome over the whole cloud
    # at two sizes: small for the puff scallops, large for volume), so the
    # inside of the cloud can never show holes or blobs
    hg = 0.5 * blur(M, 7 * scale * S2) + 0.5 * blur(M, 34 * scale * S2)
    gyy, gxx = np.gradient(hg)
    kk = 70.0 * S2
    ng = np.sqrt((gxx * kk) ** 2 + (gyy * kk) ** 2 + 1)
    dot_g = (-gxx * kk * lx - gyy * kk * ly + lz) / ng
    t_lit = ((dot_g > th) & ~under).astype(np.float32)
    t_hi = ((dot_g > 0.90) & ~under).astype(np.float32)
    t_lit = (blur(t_lit, 2 * S2) > 0.5).astype(np.float32)
    t_hi = (blur(t_hi, 2 * S2) > 0.5).astype(np.float32) * t_lit
    # the shade gets a soft lift toward the bottom (light bouncing off the haze)
    lift = smoothstep(base - height * 0.4, base + 40 * scale, gy_)[..., None] * 0.35
    col = mix(mix(shade, haze, lift), lit, t_lit[..., None])
    col = mix(col, hi if hi is not None else lit, t_hi[..., None])

    def down(a):
        return a.reshape(ph // S2, S2, pw // S2, S2, *a.shape[2:]).mean(axis=(1, 3))
    Md = down(M)
    cd = down(col * M[..., None]) / np.maximum(Md[..., None], 1e-4)
    over(img[y0:y1, x0:x1], Md, cd)
    return img


def m_skyclouds(p: Pal, rng):
    # light comes from the upper left (moon at night, sun by day)
    lx_, ly_ = W * 0.20, H * 0.16
    L3 = (-0.55, -0.55, 0.63)
    if p.dark:
        hazec = mix(p.c2, p.accent, 0.55)
        img = vgrad([(0, p.c0 * 0.85), (0.32, p.c1), (0.62, mix(p.c1, p.c2, 0.8)), (1.0, hazec)])
        st = stars(rng, 1100, H * 0.5) * smoothstep(H * 0.5, H * 0.05, YY) * 0.8
        img = screen(img, st[..., None] * p.hot)
        d = np.sqrt((XX - lx_) ** 2 + (YY - ly_) ** 2)
        moon = np.clip(46 - d + 0.5, 0, 1)
        img = screen(img, (blur(moon, 50) * 0.8 + blur(moon, 260) * 0.7)[..., None] * p.accent * 0.6)
        img = over(img, moon, p.hot)
        lit = mix(p.accent, p.hot, 0.55)
        shade = mix(p.c1, p.c2, 0.70)
    else:
        hazec = p.c0
        img = vgrad([(0, mix(p.c2, p.accent, 0.20)), (0.5, mix(p.c2, p.c1, 0.6)), (1.0, p.c0)])
        d = np.sqrt((XX - lx_) ** 2 + (YY - ly_) ** 2)
        img = screen(img, (np.exp(-d / 150) * 0.8 + np.exp(-d / 650) * 0.35)[..., None] * np.ones(3))
        lit = mix(np.ones(3, np.float32), p.c1, 0.55)
        shade = mix(p.c1, p.c2, 0.80)

    def tones(depth):  # depth 0 = far (hazy) .. 1 = near
        return mix(hazec, lit, 0.35 + 0.65 * depth), mix(hazec, shade, 0.25 + 0.75 * depth)
    hi_ = mix(lit, p.hot, 0.6) if p.dark else np.ones(3, np.float32)

    # 1) small, high, far clouds: flat little cumulus
    for x, y, w in [(0.62, 0.30, 300), (0.80, 0.42, 220), (0.13, 0.44, 260), (0.42, 0.20, 190)]:
        x = (x + rng.uniform(-0.03, 0.03)) * W
        y = (y + rng.uniform(-0.02, 0.02)) * H
        hgt = w * rng.uniform(0.30, 0.38)
        pf = _cumulus_puffs(rng, x, y, w, hgt, 0.28)
        lt, sh = tones(0.35)
        _paint_cloud(img, pf, y, hgt, 0.28, lt, sh, hazec, L3, rng=rng, hi=hi_)
    img = over(img, smoothstep(H * 0.1, H * 0.9, YY) * 0.12, hazec)

    # 2) a low row of distant clouds along the horizon
    x = -100.0
    while x < W + 100:
        w = rng.uniform(260, 420)
        hgt = w * rng.uniform(0.35, 0.55)
        pf = _cumulus_puffs(rng, x, H * 0.84, w, hgt, 0.55)
        lt, sh = tones(0.45)
        _paint_cloud(img, pf, H * 0.84, hgt, 0.55, lt, sh, hazec, L3, rng=rng, hi=hi_)
        x += w * rng.uniform(0.75, 1.0)
    img = over(img, smoothstep(H * 0.55, H * 0.95, YY) * 0.35, hazec)

    # 3) the main towers rising from the lower third (tallest left of centre,
    #    to balance the pole on the right)
    towers = [(0.36, 1.00, 1.00, 0.35), (0.72, 0.70, 0.85, -0.3), (0.04, 0.60, 0.75, 0.5)]
    base = H * 1.02
    for tx, th_, depth, lean in sorted(towers, key=lambda t: t[2]):
        width = W * 0.44 * (0.70 + 0.30 * th_)
        hgt = H * 0.60 * th_
        cx = (tx + rng.uniform(-0.02, 0.02)) * W
        pf = _cumulus_puffs(rng, cx, base, width, hgt, 1.0, lean)
        lt, sh = tones(depth)
        _paint_cloud(img, pf, base, hgt, 1.0, lt, sh, hazec, L3, rng=rng, hi=hi_)
    # a haze bank along the bottom: the tower bases dissolve into it
    img = over(img, smoothstep(H * 0.74, H * 1.0, YY) * 0.80, hazec)

    # 4) the pole and wires: a quiet accent at the far right
    ink = mix(p.c0 * 0.55, hazec, 0.18) if p.dark else mix(p.c2, p.c4, 0.55)
    px = W * 0.915

    def pole(dr, s):
        dr.polygon([((px - 10) * s, H * s), ((px - 6) * s, H * 0.26 * s),
                    ((px + 6) * s, H * 0.26 * s), ((px + 10) * s, H * s)], fill=255)
        arms = [(H * 0.30, 120), (H * 0.36, 90)]
        for yy_, half in arms:
            dr.rectangle([(px - half) * s, yy_ * s, (px + half) * s, (yy_ + 9) * s], fill=255)
        for k, (yy_, half) in enumerate(arms):
            for ix in (-half + 12, half - 12) if k else (-half + 12, 0, half - 12):
                x0_, y0_ = px + ix, yy_ - 2
                x1_, y1_ = -40, y0_ + 70 + k * 50 + ix * 0.2
                sag = 120 + 25 * k
                pts = [((x0_ + (x1_ - x0_) * t) * s, (y0_ + (y1_ - y0_) * t + sag * 4 * t * (1 - t)) * s)
                       for t in np.linspace(0, 1, 80)]
                dr.line(pts, fill=255, width=max(1, int(1.8 * s)))
    img = over(img, shape_mask(pole) * 0.92, ink)

    # 5) a few petals drifting down (tinted with the theme's accent)
    if p.dark or float(p.accent.max() - p.accent.min()) >= 0.12:  # grey themes: none (they read as dust)
        pet = mix(p.accent, p.hot, 0.5) if p.dark else mix(p.accent, p.c1, 0.3)
        for count, smin, smax, bl, op in [(26, 6, 10, 0, 0.75), (9, 12, 18, 0, 0.8), (2, 28, 38, 5, 0.5)]:
            def petals(dr, s, count=count, smin=smin, smax=smax):
                for _ in range(count):
                    y = rng.uniform(0.05, 0.95) * H
                    x = (rng.uniform(0.25, 0.95) * W + (H - y) * 0.4) % W
                    sz = rng.uniform(smin, smax)
                    ang = rng.uniform(0, math.tau)
                    squash = rng.uniform(0.35, 1.0)
                    pts = []
                    for j in range(40):
                        t = j / 40 * math.tau
                        rr = 1.0 - 0.28 * max(0.0, math.cos(t)) ** 18
                        a_, b_ = math.cos(t) * sz * rr, math.sin(t) * sz * 0.58 * squash * (0.75 + 0.25 * math.cos(t))
                        pts.append(((x + a_ * math.cos(ang) - b_ * math.sin(ang)) * s,
                                    (y + a_ * math.sin(ang) + b_ * math.cos(ang)) * s))
                    dr.polygon(pts, fill=255)
            m = shape_mask(petals)
            if bl:
                m = blur(m, bl)
            img = over(img, np.clip(m, 0, 1) * op, pet)

    return vignette(img, 0.30) if p.dark else vignette(img, 0.06, p.c2)


MOTIFS = {
    "synthwave": m_synthwave,
    "skyline": m_skyline,
    "mountains": m_mountains,
    "circuit": m_circuit,
    "skyclouds": m_skyclouds,
}


def render(pal: Pal, motif: str, seed: int = 7) -> Image.Image:
    rng = np.random.default_rng(seed)
    img = MOTIFS[motif](pal, rng).astype(np.float32)
    return finish(np.clip(img, 0, 1), rng, grain=0.010 if pal.dark else 0.006)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--palette", choices=sorted(PALETTES))
    ap.add_argument("--colors", nargs="+", help="hex colours (any order); roles are picked by brightness")
    ap.add_argument("--mode", choices=["dark", "light"])
    ap.add_argument("--motif", choices=sorted(MOTIFS))
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", help="output PNG path")
    ap.add_argument("--preview", type=int, default=640, help="also write a preview this wide (0 = none)")
    ap.add_argument("--samples", action="store_true", help="render the research sample set")
    a = ap.parse_args(argv)

    here = os.path.dirname(os.path.abspath(__file__))
    jobs = []
    if a.samples:
        for pn in ("purple", "white", "darkblue"):
            for mo in MOTIFS:
                jobs.append((Pal(PALETTES[pn]), mo, os.path.join(here, "samples", f"{pn}-{mo}.png")))
    else:
        if not a.motif or not (a.palette or a.colors):
            ap.error("give --motif and --palette or --colors (or --samples)")
        pal = Pal(PALETTES[a.palette]) if a.palette else Pal.from_colors(a.colors, a.mode)
        name = a.palette or "custom"
        jobs.append((pal, a.motif, a.out or os.path.join(here, "samples", f"{name}-{a.motif}.png")))
    for pal, mo, out in jobs:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = render(pal, mo, a.seed)
        im.save(out, optimize=True)
        if a.preview:
            pv = im.resize((a.preview, a.preview * H // W), Image.LANCZOS)
            pv.save(out[:-4] + ".preview.png", optimize=True)
        print("wrote", out, file=sys.stderr)


if __name__ == "__main__":
    main()
