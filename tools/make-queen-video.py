#!/usr/bin/env python3
"""Encode the River View Queen film for the homepage bedroom card.

THE FOOTAGE. Dropbox/River Penthouse Edited/
dji_export_20260923_185704_1791245580832_editor.mp4, added by Matt on
21 October 2026: 31 seconds, 3840x2160 HEVC in HDR (HLG, BT.2020). The camera
glides in past the queen bed and the chaise to the spotting scope at the
window, then out over the river at dusk.

HDR TO SDR. Browsers that don't do HDR show HLG washed out, and this ffmpeg
has no tone mapping filters (zscale, libplacebo), so macOS's own avconvert
does it first: exporting to its H.264 1920x1080 preset tone-maps to BT.709.

THE WINDOW. 2.5s to 20.5s: from the bed, windows and scope in full view to
the river; after about 21s the picture barely moves as the light goes.
Forward then backward, like the hero (make-hero-video.py), so the loop has
no seam: 36 seconds. 960 wide fills the card (16:10, at most ~600px wide)
on any screen; silent. The poster is the window's first frame.

Usage:  python3 tools/make-queen-video.py
"""
import io, os, subprocess, tempfile
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(REPO, 'riverpenthouse', 'img')
MASTER = os.path.expanduser('~/Library/CloudStorage/Dropbox/River Penthouse Edited/'
                            'dji_export_20260923_185704_1791245580832_editor.mp4')
START, LENGTH, WIDTH, CRF = 2.5, 18.0, 960, 32

sdr = os.path.join(tempfile.mkdtemp(), 'queen-sdr.mov')
subprocess.run(['avconvert', '-s', MASTER, '-p', 'Preset1920x1080', '-o', sdr, '--replace'],
               check=True, capture_output=True)

graph = (f'[0:v]scale={WIDTH}:-2:flags=lanczos,split[a][b];[b]reverse[r];'
         '[a][r]concat=n=2:v=1:a=0,format=yuv420p[v]')
out = os.path.join(IMG, 'queen-film.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(START), '-t', str(LENGTH), '-i', sdr,
                '-filter_complex', graph, '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'veryslow',
                '-crf', str(CRF), '-profile:v', 'high', '-color_primaries', 'bt709',
                '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', out], check=True)

png = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(START), '-i', sdr, '-frames:v', '1',
                      '-vf', 'scale=1200:-2:flags=lanczos', '-f', 'image2pipe', '-c:v', 'png', '-'],
                     capture_output=True, check=True).stdout
poster = os.path.join(IMG, 'queen-film.webp')
Image.open(io.BytesIO(png)).convert('RGB').save(poster, 'WEBP', quality=80, method=6)
for f in (out, poster):
    print(f'{os.path.basename(f)}: {os.path.getsize(f) / 1e6:.2f} MB')
