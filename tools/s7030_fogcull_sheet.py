#!/usr/bin/env python3
"""s7030: owner sheet for a FOGCULL=tog3 capture: rows = 6 moments in flight; columns = last k=a frame, first k=b and k=c frames
after it (adjacent seconds, phase 0.3-0.7 of each second, so the camera barely moved). Usage: s7030_fogcull_sheet.py raw out.png [labels]"""
import sys, struct
from PIL import Image, ImageDraw
raw, out = sys.argv[1], sys.argv[2]; lab = (sys.argv[3] if len(sys.argv) > 3 else "k=0,k=1,k=0.5").split(',')
f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec
best = {}
for i in range(n):
    f.seek(i * rec); t, _, _ = struct.unpack('<QII', f.read(16)); s = t / 24e6
    if abs(s % 1 - 0.5) < 0.2: best.setdefault(int(s), i)
secs = sorted(best); trip = [s for s in secs if s % 3 == 0 and s + 1 in best and s + 2 in best]
pick = [trip[int(j * (len(trip) - 1) / 5)] for j in range(6)] if len(trip) >= 6 else trip
S = Image.new('RGB', (3 * w, len(pick) * (h + 14)), 'black'); d = ImageDraw.Draw(S)
for r, s in enumerate(pick):
    for c in range(3):
        f.seek(best[s + c] * rec + 16); im = Image.frombytes('RGB', (w, h), f.read(w * h * 3)); S.paste(im, (c * w, r * (h + 14) + 14))
        d.text((c * w + 4, r * (h + 14)), "%s  t=%d s" % (lab[c], s + c), fill='white')
S.save(out); print("rows", len(pick), "secs", pick)
