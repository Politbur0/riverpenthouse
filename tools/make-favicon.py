#!/usr/bin/env python3
"""The favicon set: Cornelius, the Hilltop kingfisher, in the gold of this
site on its river blue, inside a gold ring. The same bird and layout as
stayathilltop.com's favicon (hilltop-site/tools/make-favicon.py), in River
Penthouse colours so the two tabs are told apart.

    python3 tools/make-favicon.py

Needs rsvg-convert (brew install librsvg) and Pillow. The bird comes from
tools/cornelius.svg, a copy of hilltop-site/src/assets/marks/kingfisher.svg.

Writes into riverpenthouse/ (the folder Vercel serves):
  favicon.svg            what modern browsers use
  favicon.ico            16, 32 and 48, the fallback
  favicon-*.png, favicon.png, android-icon-192x192.png, icon-512x512.png
                         round, transparent corners
  apple-touch-icon.png, apple-icon-*.png, ms-icon-144x144.png, icon-*.png
                         square and opaque, no ring: a home screen rounds the
                         corners itself and shows no transparency
Every older file keeps its name and size, so nothing that links to one breaks."""
import io, os, re, subprocess, tempfile
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, 'riverpenthouse')
GROUND, GOLD = '#3d6170', '#dcb57e'   # --river-deep and --gold-light
K = re.search(r' d="([^"]+)"', open(os.path.join(REPO, 'tools', 'cornelius.svg')).read()).group(1)

def svg(ring=True, bird=0.67, square=False):
    """512 square, the bird's 235x295 box centred both ways."""
    h = 512 * bird; s = h / 295; w = 235 * s
    x, y = 256 - w / 2, 256 - h / 2
    ground = (f'<rect width="512" height="512" fill="{GROUND}"/>' if square else
              f'<circle cx="256" cy="256" r="256" fill="{GROUND}"/>')
    ring_el = f'<circle cx="256" cy="256" r="240" fill="none" stroke="{GOLD}" stroke-width="18"/>' if ring else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="River Penthouse">'
            f'{ground}{ring_el}<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})" fill="{GOLD}" fill-rule="evenodd">'
            f'<path d="{K}"/></g></svg>')

TMP = tempfile.mkdtemp()
def render(markup, px):
    f = os.path.join(TMP, 'icon.svg'); open(f, 'w').write(markup)
    out = subprocess.run(['rsvg-convert', '-w', str(px), '-h', str(px), f], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(out)).convert('RGBA')

ROUND, SQUARE = svg(), svg(ring=False, bird=0.7, square=True)
open(os.path.join(SITE, 'favicon.svg'), 'w').write(ROUND + '\n')

round_pngs = {'favicon-16x16.png': 16, 'favicon-16x16-dark.png': 16, 'favicon-16x16-light.png': 16,
              'favicon-32x32.png': 32, 'favicon.png': 32, 'favicon-48x48.png': 48, 'favicon-96x96.png': 96,
              'android-icon-192x192.png': 192, 'icon-512x512.png': 512}
square_pngs = {'apple-touch-icon.png': 180, 'ms-icon-144x144.png': 144,
               'icon-560x560.png': 560, 'icon-1024x1024.png': 1024, 'icon-1200x1200.png': 1200,
               **{f'apple-icon-{n}x{n}.png': n for n in (57, 60, 72, 76, 114, 120, 144, 152, 180)}}
for name, px in round_pngs.items():
    render(ROUND, px).save(os.path.join(SITE, name), optimize=True)
for name, px in square_pngs.items():
    render(SQUARE, px).convert('RGB').save(os.path.join(SITE, name), optimize=True)

# The .ico: each size drawn at that size rather than shrunk from a big one.
sizes = [16, 32, 48]
frames = [render(ROUND, n) for n in sizes]
frames[-1].save(os.path.join(SITE, 'favicon.ico'), sizes=[(n, n) for n in sizes], append_images=frames[:-1])
print(f'favicon.svg, favicon.ico, {len(round_pngs)} round and {len(square_pngs)} square PNGs')
