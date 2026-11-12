#!/usr/bin/env python3
"""s7163: coordinate-descent refit of the presented capture rect on a SUBSET of swaps (e.g. flight only), reusing the
presented-frame pairing already chosen by s7122_fidelity score (frames.csv pframe column), so each candidate rect costs
one crop+resize+diff per sampled swap instead of a full rescore.

usage: s7163_rectfit.py raw aldir frames.csv x0,y0,x1,y1 [--every n] [--swap-lo a] [--swap-hi b] [--step 1] [--slack 2]
prints the objective (mean frac>T over sampled swaps, central band split 46,322 also reported) for the start rect and the
best rect found. Positive control: the start rect +4 px on x0 must score worse than the start rect (printed as CTRL).
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('fid', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py'))
fid = importlib.util.module_from_spec(spec); spec.loader.exec_module(fid)
from PIL import Image

a = sys.argv[1:]; raw = fid.Raw(a[0]); aldir = a[1]; fcsv = a[2]; rect0 = tuple(map(int, a[3].split(',')))
opt = dict(zip(a[4::2], a[5::2])); every = int(opt.get('--every', 4)); lo = int(opt.get('--swap-lo', 0))
hi = int(opt.get('--swap-hi', 1 << 62)); step = int(opt.get('--step', 1))
slack = int(opt.get('--slack', 2))  # s7188: how far the rect may run past the capture (picture cropped by the window)
rows = [r for r in csv.DictReader(open(fcsv)) if lo <= int(r['swap']) < hi][::every]
pairs = []
for r in rows:
    im = fid.load_al(os.path.join(aldir, 'f%s.rgb' % r['swap']))
    if im: pairs.append((im, raw.img(int(r['pframe']))))
W, H = 370, 207  # compare size fixed (the s7160 refit rect size) so candidates are comparable
als = [p[0].resize((W, H), Image.BOX) for p in pairs]


def obj(rect):
    tot = 0.0; totc = 0.0
    for al, pr in zip(als, (p[1] for p in pairs)):
        d = fid.dmap(al, pr.crop(rect).resize((W, H), Image.BOX))
        tot += sum(1 for v in d if v > fid.T) / len(d)
        totc += sum(1 for y in range(H) for v in d[y * W + 46:y * W + 322] if v > fid.T) / (H * 276)
    return tot / len(als), totc / len(als)


cur = rect0; best = obj(cur); print('start', cur, 'frac %.4f centre %.4f n %d' % (best + (len(als),)))
ctrl = obj((cur[0] + 4,) + cur[1:]); print('CTRL x0+4 frac %.4f centre %.4f %s' % (ctrl + ('PASS' if ctrl[0] > best[0] else 'FAIL',)))
improved = True
while improved:
    improved = False
    for k in range(4):
        for dv in (-step, step):
            c = list(cur); c[k] += dv; c = tuple(c)
            if c[2] - c[0] < 100 or c[3] - c[1] < 60 or c[0] < 0 or c[1] < 0 or c[2] > raw.w + slack or c[3] > raw.h + slack: continue
            s = obj(c)
            if s[0] < best[0] - 1e-5: best, cur, improved = s, c, True; print('  ->', cur, 'frac %.4f centre %.4f' % best)
print('best', ','.join(map(str, cur)), 'frac %.4f centre %.4f' % best)
