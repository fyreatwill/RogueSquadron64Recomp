#!/usr/bin/env python3
"""s7128 positive controls for s7128_pixel.py. (1) capture scale: paint the fire's corner->base path 1 px wide at 50% darkness into the
presented frame and re-measure line vs control (must rise well above the unpainted value). (2) native: the angrylion replay at 796x448,
line vs +-3 px control luminance (does the hardware draw anything visible along the wedge?).
usage: s7128_ctl.py raw aldir pos.txt swap pframe x0,y0,x1,y1"""
import sys, os, importlib.util
from PIL import Image
spec = importlib.util.spec_from_file_location('fid', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py'))
fid = importlib.util.module_from_spec(spec); spec.loader.exec_module(fid)
raw, aldir, posp, s, pf, rect = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), tuple(map(int, sys.argv[6].split(',')))
W, H = rect[2] - rect[0], rect[3] - rect[1]
alN = fid.load_al(os.path.join(aldir, 'f%d.rgb' % s)); aw, ah = alN.size; al = alN.resize((W, H), Image.BOX)
P = fid.Raw(raw).img(pf).crop(rect)
lum = lambda p: (p[0] * 3 + p[1] * 6 + p[2]) / 10.0
for l in open(posp):
    p = l.split(); v = [(float(p[i]), float(p[i + 1])) for i in (1, 3, 5)]
    c = v[0]; b = ((v[1][0] + v[2][0]) / 2, (v[1][1] + v[2][1]) / 2)
    dx, dy = b[0] - c[0], b[1] - c[1]; L = (dx * dx + dy * dy) ** .5; nx, ny = -dy / L, dx / L
    def path(sc_x, sc_y, off, w, h):
        out = []
        for q in range(800):
            f = q / 800; x, y = c[0] + dx * f + off * nx, c[1] + dy * f + off * ny
            X, Y = int(x * sc_x), int(y * sc_y)
            if 0 <= x < aw and 0 <= y < ah and 0 <= X < w and 0 <= Y < h: out.append((X, Y))
        return list(dict.fromkeys(out))
    ln = path(W / aw, H / ah, 0, W, H); ct = path(W / aw, H / ah, 6, W, H) + path(W / aw, H / ah, -6, W, H)
    Q = P.copy()
    for z in ln: Q.putpixel(z, tuple(int(x * 0.5) for x in Q.getpixel(z)))
    def dl(img):
        d = fid.dmap(al, img); return sum(d[y * W + x] for x, y in ln) / len(ln), sum(d[y * W + x] for x, y in ct) / len(ct)
    n0 = path(1, 1, 0, aw, ah); n1 = path(1, 1, 3, aw, ah) + path(1, 1, -3, aw, ah)
    m = lambda im, pts: sum(lum(im.getpixel(z)) for z in pts) / len(pts)
    print('tick %s corner %s: capture d line/ctl real %.1f/%.1f painted %.1f/%.1f | native AL lum line %.1f ctl %.1f (n=%d)' %
          (p[0], c, *dl(P), *dl(Q), m(alN, n0), m(alN, n1), len(n0)))
