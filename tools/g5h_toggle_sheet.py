#!/usr/bin/env python3
"""s6921 G5h: owner sheet from g5h_toggle_rank top rows: the frames G before and after each listed toggle, side by side, labelled lever off / on.
  g5h_toggle_sheet.py RAW OUT.png G frame:to [frame:to ...]   (to = state entered at the toggle, 1 = lever on)"""
import struct, sys
from PIL import Image, ImageDraw
raw, out, G = sys.argv[1], sys.argv[2], int(sys.argv[3]); rows = [tuple(map(int, x.split(':'))) for x in sys.argv[4:]]
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3
def fr(i):
    f.seek(i * rec); t = struct.unpack('<Q', f.read(8))[0]; f.seek(i * rec + 16); return (t - t0) / 24e6, Image.frombytes('RGB', (w, h), f.read(w * h * 3))
tw = 512; th = tw * h // w; im = Image.new('RGB', (tw * 2, (th + 14) * len(rows)), (20, 20, 20)); d = ImageDraw.Draw(im)
for k, (i, to) in enumerate(rows):
    for j, on in ((i - G, 1 - to), (i + G, to)):
        x = on; t, g = fr(j); im.paste(g.resize((tw, th)), (x * tw, k * (th + 14) + 14)); d.text((x * tw + 3, k * (th + 14) + 1), f'{"on" if on else "off"} t={t:.2f}', fill=(255, 255, 0))
im.save(out)
