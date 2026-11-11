#!/usr/bin/env python3
"""s7122 G3 retail-settings fidelity: RT64 presented frames vs angrylion replays of the SAME forwarded RDP stream.

One run (scratch/s7122/arm.zsh) gives: cap (ROGUESQ_G5B_FRAME), raw (g5b_capture of the window), and replays
(frame_replay -> aldir/f<swap>.rgb). Per replayed swap the presented frame is matched (display lag calibrated on the
median, then best of +-2 frames), the presented content rectangle is box-scaled to the angrylion size, and the per-pixel
difference d = (|dR|+|dG|+|dB|)/3 is thresholded at T (40). Connected regions (4-conn) of the mask with area >= AMIN px
are tabulated: area, bbox, mean d, mean RGB on each side. Also a row profile of mean d (the H-fog horizon band test).

usage:
  s7122_fidelity.py score raw idx aldir out_prefix [--rect x0,y0,x1,y1] [--t0 mach] [--t1 mach]
  (s7141: --split cx0,cx1 adds central-band vs side-band columns to frames.csv; --shift n mis-pairs by n presented frames = positive control)
  s7122_fidelity.py control aldir         (positive control: paint 20x20 into a replay; must give exactly one 400 px region)
Writes out_prefix.frames.csv, out_prefix.regions.csv, out_prefix.rows.csv. Pure python + PIL (no numpy on this host).
"""
import sys, os, struct, bisect, statistics
from PIL import Image

T = 40
AMIN = 64


def load_al(path):
    d = open(path, 'rb').read(); w, h = struct.unpack('<II', d[:8]); px = d[8:]
    rows = [y for y in range(h) if sum(1 for x in range(0, w, 8) if px[(y * w + x) * 3:(y * w + x) * 3 + 3] != b'\xf8\x00\xf8') > (w // 8) // 2]
    if not rows: return None
    y0, y1 = rows[0], rows[-1] + 1
    return Image.frombytes('RGB', (w, y1 - y0), px[y0 * w * 3:y1 * w * 3])


class Raw:
    def __init__(self, path):
        self.f = open(path, 'rb'); t, self.w, self.h = struct.unpack('<QII', self.f.read(16))
        self.rec = 16 + self.w * self.h * 3; n = os.path.getsize(path) // self.rec; self.T = []
        for i in range(n):
            self.f.seek(i * self.rec); self.T.append(struct.unpack('<Q', self.f.read(8))[0])
    def img(self, i):
        self.f.seek(i * self.rec + 16)
        return Image.frombytes('RGB', (self.w, self.h), self.f.read(self.w * self.h * 3))


def dmap(a, b):
    """per-pixel mean abs RGB diff as a bytes object (len w*h)"""
    ra, ga, ba = a.split(); rb, gb, bb = b.split()
    from PIL import ImageChops
    dr = ImageChops.difference(ra, rb); dg = ImageChops.difference(ga, gb); db = ImageChops.difference(ba, bb)
    s = ImageChops.add(ImageChops.add(dr.point(lambda v: v // 3), dg.point(lambda v: v // 3)), db.point(lambda v: v // 3))
    return s.tobytes()


def regions(d, w, h, a=None, b=None):
    m = bytearray(1 if v > T else 0 for v in d); out = []
    pa = a.tobytes() if a else None; pb = b.tobytes() if b else None
    for start in range(w * h):
        if m[start] != 1: continue
        st = [start]; m[start] = 2; px = []
        while st:
            i = st.pop(); px.append(i); x, y = i % w, i // w
            for j, ok in ((i - 1, x > 0), (i + 1, x < w - 1), (i - w, y > 0), (i + w, y < h - 1)):
                if ok and m[j] == 1: m[j] = 2; st.append(j)
        if len(px) < AMIN: continue
        xs = [i % w for i in px]; ys = [i // w for i in px]; n = len(px)
        r = dict(area=n, x0=min(xs), y0=min(ys), x1=max(xs) + 1, y1=max(ys) + 1, md=sum(d[i] for i in px) / n)
        if pa:
            for k, p in (('a', pa), ('b', pb)):
                r[k] = tuple(int(sum(p[i * 3 + c] for i in px) / n) for c in range(3))
        out.append(r)
    return sorted(out, key=lambda r: -r['area'])


def fit(pres, rect, size):
    return pres.crop(rect)


def score(rawp, idx, aldir, outp, rect=None, t0=0, t1=1 << 63, split=None, shift=0):
    raw = Raw(rawp); sw = {}
    for line in open(idx):
        s, m, *_ = map(int, line.split()); sw[s] = m
    al = {}
    for fn in os.listdir(aldir):
        if fn.startswith('f') and fn.endswith('.rgb'):
            s = int(fn[1:-4])
            if s in sw and t0 <= sw[s] <= t1:
                im = load_al(os.path.join(aldir, fn))
                if im: al[s] = im
    ks = sorted(al); alsize = al[ks[0]].size
    if rect is None: rect = (0, 0, raw.w, raw.h)
    size = (rect[2] - rect[0], rect[3] - rect[1]); W, H = size  # compare at PRESENTED resolution: angrylion box-downscaled
    for s in ks: al[s] = al[s].resize(size, Image.BOX)
    print('presented', raw.w, raw.h, 'frames', len(raw.T), 'replayed', len(ks), 'al size', alsize, '-> compare at', size)
    def at(m, lag): return min(bisect.bisect_left(raw.T, m + lag), len(raw.T) - 1)
    def md(a, b): d = dmap(a, b); return sum(d) / len(d)
    cache = {}
    def P(i):
        if i not in cache: cache[i] = fit(raw.img(i), rect, size)
        return cache[i]
    best = None
    for lag in range(0, 3600000, 120000):
        sc = statistics.median(md(al[s], P(at(sw[s], lag))) for s in ks[::3])
        if best is None or sc < best[0]: best = (sc, lag)
    lag = best[1]; print('lag %.1f ms median mean|d| %.2f' % (lag / 24000.0, best[0]))
    fo = open(outp + '.frames.csv', 'w'); fo.write('swap,pframe,meand,frac_over_T,nreg,biggest' + (',meand_c,frac_c,meand_s,frac_s' if split else '') + '\n')
    ro = open(outp + '.regions.csv', 'w'); ro.write('swap,area,x0,y0,x1,y1,meand,al_rgb,rt64_rgb\n')
    rowsum = [0.0] * H; nfr = 0
    for s in ks:
        i0 = at(sw[s], lag)
        cand = [(md(al[s], P(j)), j) for j in range(max(0, i0 - 2), min(len(raw.T), i0 + 3))]
        m, j = min(cand)
        if shift: j = min(max(0, j + shift), len(raw.T) - 1); m = md(al[s], P(j))  # s7141 positive control: deliberately mis-paired
        p = P(j); d = dmap(al[s], p)
        regs = regions(d, W, H, al[s], p); nfr += 1
        for y in range(H): rowsum[y] += sum(d[y * W:(y + 1) * W]) / W
        ext = ''
        if split:  # s7141: central 4:3 band columns [split[0], split[1]) vs the side bands
            cs = [0, 0, 0]; ss = [0, 0, 0]
            for y in range(H):
                row = d[y * W:(y + 1) * W]
                for x, v in enumerate(row):
                    a_ = cs if split[0] <= x < split[1] else ss
                    a_[0] += v; a_[1] += v > T; a_[2] += 1
            ext = ',%.2f,%.4f,%.2f,%.4f' % (cs[0] / cs[2], cs[1] / cs[2], ss[0] / max(1, ss[2]), ss[1] / max(1, ss[2]))
        fo.write('%d,%d,%.2f,%.4f,%d,%d%s\n' % (s, j, m, sum(1 for v in d if v > T) / len(d), len(regs), regs[0]['area'] if regs else 0, ext))
        for r in regs:
            ro.write('%d,%d,%d,%d,%d,%d,%.1f,%s,%s\n' % (s, r['area'], r['x0'], r['y0'], r['x1'], r['y1'], r['md'],
                     '/'.join(map(str, r['a'])), '/'.join(map(str, r['b']))))
    open(outp + '.rows.csv', 'w').write('row,meand\n' + ''.join('%d,%.2f\n' % (y, rowsum[y] / nfr) for y in range(H)))
    print('frames', nfr, '->', outp + '.*.csv')


def control(aldir):
    fn = sorted(f for f in os.listdir(aldir) if f.endswith('.rgb'))[0]
    a = load_al(os.path.join(aldir, fn)); W, H = a.size
    r0 = regions(dmap(a, a.copy()), W, H)
    b = a.copy(); x0, y0 = W // 3, H // 3
    for y in range(y0, y0 + 20):
        for x in range(x0, x0 + 20):
            p = a.getpixel((x, y)); b.putpixel((x, y), tuple(255 - c if abs(255 - 2 * c) > 90 else (0 if c > 127 else 255) for c in p))
    r1 = regions(dmap(a, b), W, H, a, b)
    ok = len(r0) == 0 and len(r1) == 1 and r1[0]['area'] == 400 and (r1[0]['x0'], r1[0]['y0']) == (x0, y0)
    print('CONTROL', fn, 'identity regions', len(r0), 'painted regions', [(r['area'], r['x0'], r['y0'], r['x1'], r['y1']) for r in r1], 'PASS' if ok else 'FAIL')


if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'control': control(a[2])
    else:
        kw = {}; rest = a[6:]
        while rest:
            k, v = rest[0], rest[1]; rest = rest[2:]
            if k == '--rect': kw['rect'] = tuple(map(int, v.split(',')))
            elif k == '--t0': kw['t0'] = int(v)
            elif k == '--t1': kw['t1'] = int(v)
            elif k == '--split': kw['split'] = tuple(map(int, v.split(',')))
            elif k == '--shift': kw['shift'] = int(v)
        score(a[2], a[3], a[4], a[5], **kw)
