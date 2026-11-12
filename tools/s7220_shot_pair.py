#!/usr/bin/env python3
"""s7220: RETINA=1 vs RETINA=0 fullscreen screenshot pairs (screencapture -x at the same wall second of the same route).
Each PNG is downscaled 4x by sips to a 24-bit BMP (pure python, no numpy). Per pair: lit bounding box (rows/cols with >2%
of pixels above luma 24) = the drawn picture's extent, so a point-size path (rect/scissor/pillarbox at half size or offset)
shows as a bbox mismatch (> 2 downscaled px = 8 screen px); plus mean abs luma diff a1 vs a0 (phase-sensitive: read it only
where a0 is static, i.e. a0 vs its previous shot < 2). Positive control: a1's first lit shot with its left quarter blanked
must report a bbox mismatch (CONTROL PASS).
usage: s7220_shot_pair.py DIR A1 A0"""
import sys, glob, re, struct, subprocess, os, tempfile
d, A, B = sys.argv[1:4]; tmp = tempfile.mkdtemp()
def load(p):
    o = os.path.join(tmp, os.path.basename(p) + '.bmp')
    w0 = int(re.search(rb'pixelWidth: (\d+)', subprocess.run(['sips', '-g', 'pixelWidth', p], capture_output=True).stdout)[1])
    h0 = int(re.search(rb'pixelHeight: (\d+)', subprocess.run(['sips', '-g', 'pixelHeight', p], capture_output=True).stdout)[1])
    subprocess.run(['sips', '-s', 'format', 'bmp', '-z', str(h0 // 4), str(w0 // 4), p, '--out', o], capture_output=True)
    b = open(o, 'rb').read(); off, = struct.unpack_from('<I', b, 10); w, h = struct.unpack_from('<ii', b, 18); bpp, = struct.unpack_from('<H', b, 28)
    k = bpp // 8; st = (w * k + 3) & ~3; H = abs(h); g = []
    for y in range(H):
        ry = H - 1 - y if h > 0 else y; r = b[off + ry * st: off + ry * st + w * k]
        g.append([(r[i] + 2 * r[i + 1] + r[i + 2]) >> 2 for i in range(0, w * k, k)])
    return g
def bbox(g):
    H, W = len(g), len(g[0]); rows = [y for y in range(H) if sum(v > 24 for v in g[y]) > 0.02 * W]
    cols = [x for x in range(W) if sum(g[y][x] > 24 for y in range(H)) > 0.02 * H]
    return (cols[0], rows[0], cols[-1], rows[-1]) if rows and cols else None
def mad(a, b): return sum(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb)) / (len(a) * len(a[0]))
ts = sorted(int(re.search(r'_(\d+)\.png', p)[1]) for p in glob.glob(f'{d}/shot_{A}_*.png'))
prev = None; bad = 0; ctl = None
print('t    a1 bbox (x0,y0,x1,y1)  a0 bbox               dbb   mad  a0_vs_prev verdict')
for t in ts:
    if not os.path.exists(f'{d}/shot_{B}_{t}.png'): continue
    g1, g0 = load(f'{d}/shot_{A}_{t}.png'), load(f'{d}/shot_{B}_{t}.png'); b1, b0 = bbox(g1), bbox(g0)
    db = max(abs(x - y) for x, y in zip(b1, b0)) if b1 and b0 else -1
    m = mad(g1, g0) if len(g1) == len(g0) else -1; s = mad(g0, prev) if prev and len(prev) == len(g0) else -1
    v = 'dark' if not (b1 and b0) else ('BBOX' if db > 2 else 'ok'); bad += v == 'BBOX'
    if ctl is None and b1:
        c = [r[:] for r in g1]; q = len(c[0]) // 4
        for r in c: r[:b1[0] + q] = [0] * (b1[0] + q)
        cb = bbox(c); ctl = 'PASS' if cb and abs(cb[0] - b1[0]) > 2 else 'FAIL'
    print('%4d %-22s %-22s %4d %6.2f %8.2f  %s' % (t, b1, b0, db, m, s, v)); prev = g0
# phase-insensitive: for each a1 shot, the a0 shot (any time) with the least mad, and its bbox delta.
# Arms drift apart on the route (menu dwell differs), so a same-second pair only means something while in phase.
print('nearest a0 match per a1 shot (any time): t1 -> t0 mad dbb')
G0 = {t: load(f'{d}/shot_{B}_{t}.png') for t in ts if os.path.exists(f'{d}/shot_{B}_{t}.png')}; nbad = 0
for t in ts:
    g1 = load(f'{d}/shot_{A}_{t}.png'); b1 = bbox(g1); best = min((mad(g1, g), u) for u, g in G0.items()); b0 = bbox(G0[best[1]])
    db = max(abs(x - y) for x, y in zip(b1, b0)) if b1 and b0 else -1; nbad += db > 2
    print('  %4d -> %4d %6.2f %4d%s' % (t, best[1], best[0], db, '  NOMATCH' if db > 2 else ''))
print('nearest-match bbox mismatches', nbad)
print('size %dx%d (4x down)  bbox mismatches %d  CONTROL %s' % (len(g1[0]), len(g1), bad, ctl))
