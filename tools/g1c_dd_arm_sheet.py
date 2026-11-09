#!/usr/bin/env python3
# s7019 G1c: contact sheet + far-terrain-fog-pixel score across separate fixed-dd arms (g5b_capture raws, <QII mach,w,h + RGB).
# usage: g1c_dd_arm_sheet.py out.png cols label=raw [label=raw ...]
# Rows = arms, columns = `cols` in-flight frames at equal fractions of each capture (cross-run: the autopilot route is the same,
# the camera is not identical, so read the sheet as "how far does terrain reach", not pixel diffs). Half size.
# Score per arm (all in-flight frames, step 4): fogpx% = share of pixels in rows 28..h/2 whose colour is within 24 (L1) of that
# frame's sky colour sampled at row 32 centre - more far terrain drawn => fewer fog/sky pixels above the horizon band.
import sys, struct
from PIL import Image, ImageDraw
out, C = sys.argv[1], int(sys.argv[2]); arms = [a.split('=', 1) for a in sys.argv[3:]]
def frames(p):
    f = open(p, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec
    return f, w, h, rec, n
def get(f, w, h, rec, i):
    f.seek(i * rec + 16); return f.read(w * h * 3)
def flight(b, w): return sum(b[(200 * w + x) * 3] for x in (5, 10, 15)) >= 30
rows = []
for lab, p in arms:
    f, w, h, rec, n = frames(p); ok = []; fog = []
    for i in range(0, n, 4):
        b = get(f, w, h, rec, i)
        if not flight(b, w): continue
        ok.append(i); o = (32 * w + w // 2) * 3; sky = b[o:o + 3]; tot = hit = 0
        for y in range(28, h // 2, 4):
            for x in range(0, w, 8):
                q = (y * w + x) * 3; tot += 1
                if abs(b[q] - sky[0]) + abs(b[q + 1] - sky[1]) + abs(b[q + 2] - sky[2]) <= 24: hit += 1
        fog.append(hit / tot)
    fog.sort()
    print(f'{lab}: frames={n} inflight_sampled={len(ok)} fogpx% mean={100*sum(fog)/max(1,len(fog)):.1f} med={100*fog[len(fog)//2] if fog else 0:.1f}')
    pick = [ok[int(len(ok) * (k + .5) / C)] for k in range(C)] if ok else []
    rows.append((lab, [Image.frombytes('RGB', (w, h), get(f, w, h, rec, i)).resize((w // 2, h // 2)) for i in pick]))
W = max(im.width for _, r in rows for im in r); H = max(im.height for _, r in rows for im in r)
sh = Image.new('RGB', (W * C, H * len(rows)), 'black'); d = ImageDraw.Draw(sh)
for j, (lab, r) in enumerate(rows):
    for k, im in enumerate(r): sh.paste(im, (k * W, j * H))
    d.text((6, j * H + 4), lab, fill='yellow')
sh.save(out); print('wrote', out)
