#!/usr/bin/env python3
"""s7214: contact sheet of g5b_capture raw frames with a luma gain, so near-black fade frames (mean luma < 10) show their geometry.
usage: s7214_gain_sheet.py out.png gain raw:frame[:label] [raw:frame[:label] ...]   (3 per row; raw header <QII t0,w,h>, records <Q t><pad8> + w*h*3)"""
import sys, struct
from PIL import Image, ImageDraw
out, gain, items = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
def get(r, i):
    f = open(r, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; f.seek(i * rec + 16)
    return Image.frombytes('RGB', (w, h), f.read(w * h * 3))
tw, th = 504, 316; rows = (len(items) + 2) // 3
S = Image.new('RGB', (tw * 3, (th + 16) * rows), (40, 40, 40)); d = ImageDraw.Draw(S)
for q, it in enumerate(items):
    p = it.split(':'); r, i = p[0], int(p[1]); lab = p[2] if len(p) > 2 else 'f%d' % i
    im = get(r, i).point(lambda v: min(255, int(v * gain))).resize((tw, th)); x, y = (q % 3) * tw, (q // 3) * (th + 16)
    S.paste(im, (x, y + 16)); d.text((x + 4, y + 2), '%s (x%g gain)' % (lab, gain), fill=(255, 255, 0))
S.save(out); print(out, len(items), 'frames')
