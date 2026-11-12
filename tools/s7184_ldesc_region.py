#!/usr/bin/env python3
"""s7184: localise the RT64-vs-angrylion excess on the LEVEL DESCRIPTION overlay (green typed text on AVAILABLE CRAFT).
Text mask = AL pixels of the text colour (G > 120, G - max(R,B) > 50; glyphs are (144,248,144)) inside the text band ROI rows
60-175, dilated 1 px. ctl_swap = a craft-info frame: its same-ROI loss is the no-text baseline.
Per sampled frame (best re-pairing +-R presented frames, presented rect box-downscaled to native): loss px (dmap > T) inside /
outside the mask, glyph-interior loss (mask px whose 8 AL neighbours are all green-ish text), and an x-scale fit of the text box
(k about the screen centre; H-rect predicts k != 1). Positive control: paint a 40x12 magenta block centred on a glyph pixel in the presented image ->
in-mask loss must rise on every frame.
usage: s7184_ldesc_region.py raw aldir frames.csv rect ldesc_lo ldesc_hi ctl_swap [n=12] [R=6]"""
import sys, os, csv, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7122_fidelity import Raw, load_al, dmap, T
from PIL import Image, ImageDraw
raw = Raw(sys.argv[1]); ald = sys.argv[2]; rect = tuple(map(int, sys.argv[4].split(',')))
lo, hi, cs = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
n = int(sys.argv[8]) if len(sys.argv) > 8 else 12; RP = int(sys.argv[9]) if len(sys.argv) > 9 else 6
allrows = list(csv.DictReader(open(sys.argv[3])))
rows = [r for r in allrows if lo <= int(r['swap']) <= hi]; rows = rows[::max(1, len(rows) // n)][:n]
ctl = load_al(os.path.join(ald, 'f%d.rgb' % cs)); w, h = ctl.size; Y0, Y1 = 60, 175

def best_pair(a, j0):
    b = None
    for j in range(max(0, j0 - RP), min(len(raw.T), j0 + RP + 1)):
        p = raw.img(j).crop(rect).resize((w, h), Image.BOX); d = dmap(a, p); f = sum(v > T for v in d)
        if b is None or f < b[0]: b = (f, j, d, p)
    return b

def xscale(p, k):  # scale image horizontally by k about x = w/2
    return p.transform(p.size, Image.AFFINE, (1 / k, 0, w / 2 * (1 - 1 / k), 0, 1, 0), Image.BILINEAR)

roi = lambda d: sum(1 for y in range(Y0, Y1) for x in range(w) if d[y * w + x] > T)
res = []; ctlpass = 0; ks = (0.97, 0.99, 1.0, 1.01, 1.03, 1.15, 1.333)
for r in rows:
    a = load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if a is None or a.size != (w, h): continue
    px = a.load(); raw_m = [False] * (w * h)
    for y in range(Y0, Y1):
        for x in range(w):
            R, G, B = px[x, y]; raw_m[y * w + x] = G > 120 and G - max(R, B) > 50
    m = list(raw_m)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if raw_m[y * w + x]:
                for o in (-1, 1, -w, w): m[y * w + x + o] = True
    if sum(m) < 200: continue
    f, j, d, p = best_pair(a, int(r['pframe']))
    ag = a.load(); inter = [False] * (w * h)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            i = y * w + x
            if raw_m[i] and all(raw_m[i + o] for o in (-1, 1, -w, w, -w - 1, -w + 1, w - 1, w + 1)): inter[i] = True
    lin = sum(1 for i in range(w * h) if m[i] and d[i] > T); lout = sum(1 for i in range(w * h) if not m[i] and d[i] > T)
    ni = sum(inter); li = sum(1 for i in range(w * h) if inter[i] and d[i] > T)
    ys = [i // w for i in range(w * h) if raw_m[i]]; xs = [i % w for i in range(w * h) if raw_m[i]]
    bx = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    kf = {}
    for k in ks:
        dk = dmap(a.crop(bx), xscale(p, k).crop(bx)); kf[k] = sum(v > T for v in dk) / len(dk)
    q = p.copy(); cx, cy = xs[len(xs) // 2], ys[len(ys) // 2]  # centred on a glyph pixel
    ImageDraw.Draw(q).rectangle((cx - 20, cy - 6, cx + 20, cy + 6), fill=(248, 0, 248))
    dq = dmap(a, q); lq = sum(1 for i in range(w * h) if m[i] and dq[i] > T); ctlpass += lq > lin
    res.append((int(r['swap']), sum(m), lin, lout, ni, li, kf, bx, roi(d), f))
cr = [x for x in allrows if int(x['swap']) == cs][0]; fc, jc, dc, pc = best_pair(ctl, int(cr['pframe']))
print('native', w, h, 'ctl swap', cs, 'frames', len(res), '| ctl (craft info, no text) ROI loss', roi(dc), 'whole', fc)
for s, nm, lin, lout, ni, li, kf, bx, rl, fw in res[:3]:
    print(' swap', s, 'mask', nm, 'box', bx, 'loss in', lin, 'out', lout, 'interior', ni, 'loss', li, 'kfit', {k: round(v, 4) for k, v in kf.items()})
med = lambda i: st.median(x[i] for x in res)
print('median: mask px %d | loss in-mask %d (%.4f of mask) | loss outside %d | glyph-interior px %d loss %d (%.4f)' % (
    med(1), med(2), st.median(x[2] / x[1] for x in res), med(3), med(4), med(5), st.median(x[5] / max(1, x[4]) for x in res)))
print('ROI loss median %d (ctl %d) | whole-frame loss median %d (ctl %d)' % (med(8), roi(dc), med(9), fc))
print('kfit text box median frac: ' + ' '.join('k%.3f=%.4f' % (k, st.median(x[6][k] for x in res)) for k in ks),
      '| best k per frame:', sorted(set(min(x[6], key=x[6].get) for x in res)))
print('CONTROL blanked text block raises in-mask loss on %d/%d -> %s' % (ctlpass, len(res), 'PASS' if ctlpass == len(res) else 'FAIL'))
