#!/usr/bin/env python3
"""s7942: find the F6 panel pad-cursor highlight band in each window screenshot and compare with the logged row rect.
Band = rows of the image whose median (B - R) over the table's middle columns exceeds a threshold (the cursor colour is
blue 0.25,0.45,0.85 at 0.55 alpha; normal rows are grey). Points -> pixels: scale = png_w / window_w; the title bar is
window_h - disp_h points at the top. PASS per shot: exactly one band, its centre inside the logged prow rect +- 1 row pad,
prow vis=1 and band inside clip. Run-level PASS also needs the band to move between shots (positive control)."""
import re, sys, os
from PIL import Image
D = sys.argv[1]
res = []
for line in open(os.path.join(D, 'shots.txt')):
    sh = int(re.search(r'shot=(\d+)', line).group(1)); row = int(re.search(r'row=(\d+)', line).group(1))
    wx, wy, ww, wh = map(int, re.search(r'win=\d+ (-?\d+) (-?\d+) (\d+) (\d+)', line).groups())
    dw, dh = map(float, re.search(r'disp=(\d+)x(\d+)', line).groups())
    m = re.search(r'prow=(-?\d+),(-?\d+),(-?\d+),(-?\d+) prow_i=(\d+) clip=(-?\d+),(-?\d+) vis=(\d)', line)
    if not m: res.append((sh, row, False, 'no prow rect logged')); continue
    px0, py0, px1, py1, pi, c0, c1, vis = map(int, m.groups())
    im = Image.open(os.path.join(D, f'shot{sh}.png')).convert('RGB'); W, H = im.size
    sc = W / ww; title = wh - dh
    # columns: from the end of the label column to ~70% width, in points -> px
    xs = [int((px1 + 10 + k * (dw * 0.6 - px1) / 40) * sc) for k in range(40)]
    ys0, ys1 = int((title + c0) * sc), int((title + c1) * sc)
    pix = im.load(); hot = []
    for y in range(max(0, ys0), min(H, ys1)):
        v = sorted(pix[x, y][2] - pix[x, y][0] for x in xs if 0 <= x < W)
        hot.append(v[len(v) // 2] > 40)
    bands = []; start = None
    for i, h in enumerate(hot + [False]):
        if h and start is None: start = i
        if not h and start is not None:
            if i - start >= 3: bands.append((ys0 + start, ys0 + i))
            start = None
    rh = (py1 - py0) * sc
    exp_c = (title + (py0 + py1) / 2) * sc
    ok = vis == 1 and pi == row and len(bands) == 1 and abs((bands[0][0] + bands[0][1]) / 2 - exp_c) <= rh
    det = (f'row={row} prow_i={pi} vis={vis} clip_px={ys0}-{ys1} prow_px={int((title+py0)*sc)}-{int((title+py1)*sc)} '
           f'bands={bands} scale={sc:.2f}')
    res.append((sh, row, ok, det, bands[0] if len(bands) == 1 else None))
for r in res: print(f'shot{r[0]} {"PASS" if r[2] else "FAIL"} {r[3]}')
cent = [((r[4][0] + r[4][1]) / 2) for r in res if len(r) > 4 and r[4]]
moved = len(set(int(c) for c in cent)) == len(cent) and len(cent) >= 2
npass = sum(1 for r in res if r[2])
print(f'tag=s7942_pad_cursor shots={len(res)} pass={npass} band_moves={int(moved)}')
print('VERDICT', 'PASS' if res and npass == len(res) and moved else 'FAIL'); sys.exit(0 if npass == len(res) and moved else 1)
