#!/usr/bin/env python3
"""s7031: per tog3 phase, pick the in-flight frames with the largest dark-grey (map-edge wall / off-map plateau) share in the upper half
and tile the top N per phase side by side (phase columns), to judge whether an off-map cull cuts a visible plateau.
Dark grey = max(RGB) < 90 and max-min < 25. Usage: s7031_dark_sheet.py raw out.png [labels] [N=6]"""
import sys, struct
from PIL import Image
raw, out = sys.argv[1], sys.argv[2]; lab = (sys.argv[3] if len(sys.argv) > 3 else "p0,p1,p2").split(','); N = int(sys.argv[4]) if len(sys.argv) > 4 else 6
f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec
sc = {0: [], 1: [], 2: []}
for i in range(0, n, 3):
    f.seek(i * rec); t, _, _ = struct.unpack('<QII', f.read(16)); b = f.read(w * h * 3)
    o = (h // 2 * w + 3) * 3
    if b[o] + b[o + 1] + b[o + 2] < 10: continue
    s = t / 24e6
    if not 0.2 <= s % 1 <= 0.8: continue
    d = k = 0
    for y in range(16, h // 2, 4):
        for x in range(0, w, 8):
            q = (y * w + x) * 3; r, g, bb = b[q], b[q + 1], b[q + 2]; k += 1
            if max(r, g, bb) < 90 and max(r, g, bb) - min(r, g, bb) < 25: d += 1
    sc[int(s) % 3].append((d / k, i, int(s)))
from PIL import ImageDraw
img = Image.new('RGB', (3 * w, N * (h + 14)))
for p in range(3):
    picks = []; used = set()
    for v, i, s in sorted(sc[p], reverse=True):
        if s in used: continue
        used.add(s); picks.append((v, i, s))
        if len(picks) == N: break
    for r, (v, i, s) in enumerate(picks):
        f.seek(i * rec + 16); im = Image.frombytes('RGB', (w, h), f.read(w * h * 3)); img.paste(im, (p * w, r * (h + 14) + 14))
        ImageDraw.Draw(img).text((p * w + 4, r * (h + 14)), '%s dark=%.2f s=%d' % (lab[p], v, s), fill=(255, 255, 0))
    print(p, lab[p], 'frames', len(sc[p]), 'top dark', ['%.2f' % x[0] for x in picks], 'mean dark %.3f' % (sum(x[0] for x in sc[p]) / max(1, len(sc[p]))))
img.save(out)
