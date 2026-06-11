"""
Regenerate brand exports from the SVG masters in visual_assets/brand/.

Run from the repo root:  python3 visual_assets/build_brand.py

Three jobs:
1. PNG exports at 2x the nominal size (supersampled — crisp on Retina; social
   platforms accept oversized uploads and downscale). qlmanage rasterizes SVGs
   as LETTERBOXED SQUARES, so non-square exports render at max dimension and
   are centre-cropped with sips.
2. The favicon ladder (spec sizes are fixed: 16/32/180/192/512 — already
   supersampled from a 1024 render, unchanged).
3. *-outlined.svg distribution copies of text-bearing masters: live <text> is
   converted to vector paths so the SVGs render identically on machines
   without Radio-Canada installed (GitHub previews, other people's laptops).
   The live-text masters remain the editable sources.

Requirements: macOS (qlmanage, sips), fontTools, and the Radio-Canada static
instances installed at ~/Library/Fonts/RadioCanada-{Regular,SemiBold,Bold}.ttf
(see brand/typography.md for the instancing recipe).
"""
import os, re, shutil, subprocess, tempfile

B = os.path.join(os.path.dirname(__file__), "brand")
TMP = tempfile.mkdtemp(prefix="brandexport")
SCALE = 2  # supersampling factor for PNG exports

# svg (relative to brand/) -> nominal (w, h); PNGs ship at SCALE x nominal
EXPORTS = {
    "social/og-card.svg":                (1200, 630),
    "social/og-card-strata.svg":         (1200, 630),
    "social/github-social-preview.svg":  (1280, 640),
    "social/x-header.svg":               (1500, 500),
    "social/linkedin-banner.svg":        (1584, 396),
    "social/linkedin-banner-strata.svg": (1584, 396),
    "social/facebook-cover.svg":         (820,  312),
    "social/instagram-card.svg":         (1080, 1080),
    "social/github-avatar.svg":          (512,  512),
    "social/avatar-cells.svg":           (1024, 1024),
    "social/avatar-strata.svg":          (1024, 1024),
    "palette-sheet.svg":                 (1200, 860),
}
FAVICON_LADDER = {"favicon.svg": [(32, "favicon-32.png"), (16, "favicon-16.png")],
                  "apple-touch.svg": [(180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")]}
# distribution copies with text outlined to paths (palette-sheet excluded: it
# mixes in Menlo for hex codes and is internal documentation, not a mark)
OUTLINE = [
    "botanical/lockup-horizontal.svg", "botanical/lockup-stacked.svg",
    "botanical/lockup-stacked-cells.svg", "botanical/wordmark-canobs.svg",
    "social/og-card.svg", "social/og-card-strata.svg",
    "social/github-social-preview.svg", "social/x-header.svg",
    "social/linkedin-banner.svg", "social/linkedin-banner-strata.svg",
    "social/facebook-cover.svg", "social/instagram-card.svg",
]

def export(svg_rel, w, h):
    svg = os.path.join(B, svg_rel)
    png = svg[:-4] + ".png"
    W, H = w * SCALE, h * SCALE
    subprocess.run(["qlmanage", "-t", "-s", str(max(W, H)), "-o", TMP, svg],
                   capture_output=True, check=False)
    shutil.copy(os.path.join(TMP, os.path.basename(svg) + ".png"), png)
    if w != h:
        subprocess.run(["sips", "-c", str(H), str(W), png, "--out", png], capture_output=True)
    print(f"  {os.path.relpath(png, B)}  {W}x{H} (2x of {w}x{h})")

# ---- text -> path outlining ------------------------------------------------
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

_FONTDIR = os.path.expanduser("~/Library/Fonts")
_WEIGHTS = {None: "Regular", "400": "Regular", "600": "SemiBold", "700": "Bold"}
_fonts = {}

def _font(weight):
    name = _WEIGHTS.get(weight, "Regular")
    if name not in _fonts:
        _fonts[name] = TTFont(os.path.join(_FONTDIR, f"RadioCanada-{name}.ttf"))
    return _fonts[name]

_TEXT_RE = re.compile(r'<text ([^>]*)>([^<]*)</text>')
_ATTR_RE = re.compile(r'([a-z-]+)="([^"]*)"')

def _outline_text(m):
    attrs = dict(_ATTR_RE.findall(m.group(1)))
    content = m.group(2)
    f = _font(attrs.get("font-weight"))
    upm = f["head"].unitsPerEm
    size = float(attrs["font-size"])
    s = size / upm
    ls = float(attrs.get("letter-spacing", 0)) / s  # px -> font units
    cmap, hmtx, gset = f.getBestCmap(), f["hmtx"], f.getGlyphSet()
    parts, cursor = [], 0.0
    for ch in content:
        g = cmap.get(ord(ch))
        if g is None:
            cursor += upm * 0.5 + ls
            continue
        adv = hmtx[g][0]
        if ch != " ":
            pen = SVGPathPen(gset)
            gset[g].draw(pen)
            d = pen.getCommands()
            if d:
                parts.append(f'<path transform="translate({cursor:.1f} 0)" d="{d}"/>')
        cursor += adv + ls
    # anchor width excludes the TRAILING letter-space (WebKit's behaviour)
    total_px = (cursor - (ls if content else 0)) * s
    x, y = float(attrs["x"]), float(attrs["y"])
    if attrs.get("text-anchor") == "middle":
        x -= total_px / 2
    fill = attrs.get("fill", "#000")
    return (f'<g fill="{fill}" transform="translate({x} {y}) scale({s} {-s})">'
            + "".join(parts) + "</g>")

def outline(svg_rel):
    src = open(os.path.join(B, svg_rel)).read()
    out, n = _TEXT_RE.subn(_outline_text, src)
    dst = os.path.join(B, svg_rel[:-4] + "-outlined.svg")
    open(dst, "w").write(out)
    print(f"  {os.path.relpath(dst, B)}  ({n} text runs outlined)")

if __name__ == "__main__":
    print(f"exports (at {SCALE}x):")
    for svg, (w, h) in EXPORTS.items():
        export(svg, w, h)
    print("favicon ladder:")
    for svg, sizes in FAVICON_LADDER.items():
        srcf = os.path.join(B, "favicon", svg)
        subprocess.run(["qlmanage", "-t", "-s", "1024", "-o", TMP, srcf], capture_output=True)
        big = os.path.join(TMP, svg + ".png")
        for n, outname in sizes:
            dst = os.path.join(B, "favicon", outname)
            shutil.copy(big, dst)
            subprocess.run(["sips", "-z", str(n), str(n), dst, "--out", dst], capture_output=True)
            print(f"  favicon/{outname}  {n}x{n}")
    print("outlined distribution copies:")
    for svg in OUTLINE:
        outline(svg)
    print("done")
