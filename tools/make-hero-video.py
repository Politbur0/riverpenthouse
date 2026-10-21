#!/usr/bin/env python3
"""Encode the homepage hero film: the walk up to the Penthouse door.

THE FOOTAGE. Dropbox/River Penthouse Edited/compose_video_1789420271261.mp4,
added by Matt on 21 October 2026: 26 seconds, 2688x1512, 30fps, one shot.
The camera starts on the lanterns and pushes slowly down the passage to the
door (44), the gate and the river beyond.

FORWARD, THEN BACKWARD, the way stayathilltop.com's hero does it
(hilltop-site/tools/make-home-hero.py): a straight loop would jump from the
door back to the lanterns; played forward then reversed, the end of the file
is its own beginning, so the loop has no seam. Nothing is generated; the
reversed half is encoded because browsers don't play video backwards.

TWO FILES. Wide (screens over 700px) is the whole frame. Narrow (phones) is
cut to the part of the frame that matters, the river, the gate and the door,
so a phone isn't sent the dark wall on the right to throw away. Both silent,
52 seconds a loop, about 2 MB wide and 1.2 MB narrow: heavy for a hero, so
the page fetches the film only after everything else has loaded. Both
30fps (the push is slow, and 24 would judder it), H.264 for every browser.

POSTERS are the exact first frame, shown before the film loads and instead
of it for anyone with reduced motion or a data saver on, so the swap cannot
jump.

Usage:  python3 tools/make-hero-video.py
"""
import io, os, subprocess
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(REPO, 'riverpenthouse', 'img')
MASTER = os.path.expanduser('~/Library/CloudStorage/Dropbox/River Penthouse Edited/'
                            'compose_video_1789420271261.mp4')
# The phone crop: x from 17.9% of the width, 1088 of 2688 wide, full height;
# about 0.72 wide to 1 tall, a phone's hero box. Keeps the river, the gate
# and the door with its 44.
NARROW_CROP = 'crop=1088:1512:480:0'
OUT = {  # name: (crop, width, crf)
    'hero-film':        (None,        1280, 35),
    'hero-film-mobile': (NARROW_CROP,  540, 36),
}

def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)

for name, (crop, width, crf) in OUT.items():
    pre = (crop + ',' if crop else '') + f'scale={width}:-2:flags=lanczos'
    graph = f'[0:v]{pre},split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0,format=yuv420p[v]'
    ff('-i', MASTER, '-filter_complex', graph, '-map', '[v]', '-an',
       '-c:v', 'libx264', '-preset', 'veryslow', '-crf', str(crf), '-profile:v', 'high',
       '-movflags', '+faststart', os.path.join(IMG, name + '.mp4'))
    poster_w = 1920 if crop is None else 900
    png = subprocess.run(['ffmpeg', '-v', 'error', '-i', MASTER, '-frames:v', '1', '-vf',
                          (crop + ',' if crop else '') + f'scale={poster_w}:-2:flags=lanczos',
                          '-f', 'image2pipe', '-c:v', 'png', '-'], capture_output=True, check=True).stdout
    Image.open(io.BytesIO(png)).convert('RGB').save(os.path.join(IMG, name + '.webp'), 'WEBP', quality=80, method=6)
    for ext in ('.mp4', '.webp'):
        f = os.path.join(IMG, name + ext)
        print(f'{name}{ext}: {os.path.getsize(f) / 1e6:.2f} MB')
