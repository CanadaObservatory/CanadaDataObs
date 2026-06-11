"""
Regenerate all PNG exports from the SVG masters in visual_assets/brand/.

Run from the repo root:  python3 visual_assets/build_brand.py

Rendering uses macOS QuickLook (qlmanage), which rasterizes SVGs as
LETTERBOXED SQUARES — non-square exports are therefore rendered at max
dimension and centre-cropped with sips. Masters with text need the brand
fonts installed locally (~/Library/Fonts/RadioCanada-{Regular,SemiBold,
Bold}.ttf — static instances of the variable font; see
brand/typography.md). The favicon PNG ladder is derived from the two
favicon SVG masters via sips resampling.
"""
import os, shutil, subprocess, tempfile

B = os.path.join(os.path.dirname(__file__), "brand")
TMP = tempfile.mkdtemp(prefix="brandexport")

# svg (relative to brand/) -> (render_px, crop_h or None for square, out png)
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

def export(svg_rel, w, h):
    svg = os.path.join(B, svg_rel)
    png = svg[:-4] + ".png"
    subprocess.run(["qlmanage", "-t", "-s", str(w), "-o", TMP, svg],
                   capture_output=True, check=False)
    shutil.copy(os.path.join(TMP, os.path.basename(svg) + ".png"), png)
    if w != h:
        subprocess.run(["sips", "-c", str(h), str(w), png, "--out", png], capture_output=True)
    print(f"  {os.path.relpath(png, B)}  {w}x{h}")

print("exports:")
for svg, (w, h) in EXPORTS.items():
    export(svg, w, h)
print("favicon ladder:")
for svg, sizes in FAVICON_LADDER.items():
    src = os.path.join(B, "favicon", svg)
    subprocess.run(["qlmanage", "-t", "-s", "1024", "-o", TMP, src], capture_output=True)
    big = os.path.join(TMP, svg + ".png")
    for n, out in sizes:
        dst = os.path.join(B, "favicon", out)
        shutil.copy(big, dst)
        subprocess.run(["sips", "-z", str(n), str(n), dst, "--out", dst], capture_output=True)
        print(f"  favicon/{out}  {n}x{n}")
print("done")
