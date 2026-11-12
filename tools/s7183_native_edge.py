#!/usr/bin/env python3
"""s7183: score RT64 vs angrylion at NATIVE fb resolution (presented rect box-downscaled to the AL size) and split the
over-threshold pixels into AL-edge vs AL-interior (edge = any 8-neighbour luma step > EDGE in the AL frame), with best re-pairing
over +-R presented frames (capture bursts mis-pair). s7182_ringint pattern, whole frame. Positive control: AL shifted 1 px right
must score worse than AL itself on every sampled frame.
usage: s7183_native_edge.py raw aldir frames.csv rect swap_lo swap_hi [n=24] [R=6]"""
import sys, os, csv, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7122_fidelity import Raw, load_al, dmap, T
from PIL import Image, ImageChops
EDGE = 40
raw = Raw(sys.argv[1]); ald = sys.argv[2]; rect = tuple(map(int, sys.argv[4].split(','))); lo, hi = int(sys.argv[5]), int(sys.argv[6])
n = int(sys.argv[7]) if len(sys.argv) > 7 else 24; RP = int(sys.argv[8]) if len(sys.argv) > 8 else 6
rows = [r for r in csv.DictReader(open(sys.argv[3])) if lo <= int(r['swap']) <= hi]; rows = rows[::max(1, len(rows) // n)][:n]
out = []; ctl = 0
for r in rows:
    a = load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if a is None: continue
    w, h = a.size; j0 = int(r['pframe']); best = None
    for j in range(max(0, j0 - RP), min(len(raw.T), j0 + RP + 1)):
        p = raw.img(j).crop(rect).resize((w, h), Image.BOX); d = dmap(a, p); f = sum(v > T for v in d) / len(d)
        if best is None or f < best[0]: best = (f, j, d, p)
    f, j, d, p = best
    sh = ImageChops.offset(a, 1, 0); fs = sum(v > T for v in dmap(sh, p)) / len(d); ctl += fs > f
    g = a.convert('L').tobytes(); e = 0; ie = 0; nl = 0
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            i = y * w + x
            if d[i] > T:
                nl += 1; c = g[i]
                if any(abs(c - g[i + o]) > EDGE for o in (-1, 1, -w, w, -w - 1, -w + 1, w - 1, w + 1)): e += 1
    out.append((int(r['swap']), f, sum(d) / len(d), e / max(1, nl), fs))
print('native', w, h, 'frames', len(out))
print('frac>40 median %.4f max %.4f | mean|d| median %.2f | loss px on AL edges median %.0f%% | 1px-shift ctl frac median %.4f' % (
    st.median(o[1] for o in out), max(o[1] for o in out), st.median(o[2] for o in out), 100 * st.median(o[3] for o in out), st.median(o[4] for o in out)))
print('CONTROL shifted AL worse on %d/%d -> %s' % (ctl, len(out), 'PASS' if ctl == len(out) else 'FAIL'))
