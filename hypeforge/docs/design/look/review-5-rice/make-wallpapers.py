#!/usr/bin/env python3
"""Make one wallpaper per theme for the rice proposal, in the theme's own colours, with the
look program's generator (~6 s each). Dark themes get synthwave suns, middle themes neon
skylines, the grays circuit boards, light themes misty mountains (anime skies picked their
cloud colours by brightness and came out wrong on light themes, 10-10).

    python3 docs/design/look/review-5-rice/make-wallpapers.py
"""
import pathlib
import subprocess
import tempfile
import tomllib

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parents[3] / "docs/research/look-2026-10"
GEN = RES / "wallpapers/generate.py"


def job(slug, t):
    m = t["meta"]
    if m["polarity"] == "light" and slug != "light-gray":
        cols = [t["surface"]["overlay"], t["surface"]["sunken"], t["band"]["soft"], t["band"]["base"], t["band"]["strong"]]
        return "mountains", "light", cols
    motif = ("circuit" if m["family"] == "neutral" and slug not in ("white", "black") else
             "skyline" if slug == "kognogos-mocha" or m["tone"] == "mid" else "synthwave")
    cols = [t["surface"]["sunken"], t["band"]["strong"], t["band"]["base"], t["band"]["text"], t["pop"]["base"]]
    return motif, "light" if m["polarity"] == "light" else "dark", cols


def main():
    d = tomllib.loads((RES / "palette/palettes.toml").read_text())
    out = HERE / "wallpapers"
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for slug in d["meta"]["order"]:
            motif, mode, cols = job(slug, d["themes"][slug])
            png = pathlib.Path(tmp) / f"{slug}.png"
            subprocess.run(["python3", str(GEN), "--colors", *[c.lstrip("#") for c in cols], "--mode", mode,
                            "--motif", motif, "--out", str(png), "--preview", "1280"], check=True, capture_output=True)
            Image.open(png.with_suffix(".preview.png")).convert("RGB").save(out / f"{slug}.jpg", quality=82, optimize=True)
            print(slug, motif)


if __name__ == "__main__":
    main()
