#!/usr/bin/env python3
"""s6903 G5d: time-labelled contact sheet of a g5b_capture .raw. usage: g5d_sheet.py x.raw out.png t0 t1 step [cols=10] [scale=0.5]; times are seconds from the first frame."""
import struct, sys, bisect
from PIL import Image, ImageDraw
raw, out = sys.argv[1], sys.argv[2]; t0, t1, st = map(float, sys.argv[3:6]); cols = int(sys.argv[6]) if len(sys.argv) > 6 else 10; sc = float(sys.argv[7]) if len(sys.argv) > 7 else .5
f = open(raw, 'rb'); b, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w*h*3
import os; n = os.path.getsize(raw)//rec; T = []
for i in range(n): f.seek(i*rec); T.append((struct.unpack('<Q', f.read(8))[0]-b)/24e6)
ts = []; t = t0
while t < t1: ts.append(t); t += st
tw, th = int(w*sc), int(h*sc); rows = (len(ts)+cols-1)//cols; S = Image.new('RGB', (cols*(tw+2), rows*(th+2)), (255, 255, 0)); d = ImageDraw.Draw(S)
for k, t in enumerate(ts):
    i = min(bisect.bisect_left(T, t), n-1); f.seek(i*rec+16)
    im = Image.frombytes('RGB', (w, h), f.read(w*h*3)).resize((tw, th)); x, y = (k % cols)*(tw+2), (k//cols)*(th+2); S.paste(im, (x, y)); d.text((x+2, y+1), f'{t:.1f}', fill=(255, 255, 0))
S.save(out)
