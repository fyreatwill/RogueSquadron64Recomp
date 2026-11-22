#!/usr/bin/env python3
"""s7827: does the port's world geometry carry the same constant Y offset as the s7826 reticle (+0.5 px = +2 RDP quanta)?

Shape-matched Y-shift census of RDP triangles, retail rdplog vs port rdplog. A triangle's SHAPE key is (PRIM, lft, DxLDy,
DxHDy, DxMDy, YM-YH, YL-YH): exact 32-bit slopes plus edge heights, independent of screen position. For every retail tri in
the retail window, every port tri in the port window with the same shape gives dy = YH_port - YH_retail (s11.2 quanta) and
dx = XH-at-common-scanline difference (px). A one-signed dy=+2 mode with dx~0 = the whole projected scene sits 0.5 px lower
(H-vp: viewport/projection centre); a dy=0 mode = world geometry exact, the reticle offset is the reticle's own (H-cpu/H-elem).
--controls: same-run planted controls on the RETAIL window vs itself: A = identity (mode must be dy 0), B = every retail tri
shifted +2 quanta in Y (mode must be +2). rc 3 on FAIL.
--pose r0:r1,p0:p1: model selection on the STATIC tri set (tris present in >=90% of the frames of each window: in lvl1
level flight that is the 42-tri sky mesh, which depends on camera ROTATION only). Paired port-vs-retail vertex offsets are fit
by three one/two-parameter models and the lowest RMS wins: H-vp (constant dy, dx=0: viewport/centre offset), H-scale (uniform
scale about the screen centre: FOV/vscale), H-pitch (camera pitch delta: dy = f*d*(1+v^2), dx = f*u*v*d, u,v = offset/f).
Same-run planted controls on the retail static set (quantised to 0.25 px like the RDP): a pitch plant must select H-pitch and
recover d, a +0.5 px constant plant must select H-vp. rc 3 on FAIL.
usage: s7827_tri_yshift_census.py RETAIL.bin[.zst] PORT.bin[.zst] --win r0:r1,p0:p1 [--controls] [--pose r0:r1,p0:p1] [--p-retail] [--pairs]
"""
import sys, os, collections, importlib.util, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rs64_zopen
a = sys.argv[1:]
if len(a) < 3 or '--win' not in a: print(__doc__); sys.exit(2)
sys.argv.append('--tri-geom')
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
tmp = tempfile.mkdtemp(prefix='s7827_')
(r0, r1), (p0, p1) = [tuple(int(v) for v in s.split(':')) for s in a[a.index('--win') + 1].split(',')]
R = m.frames(rs64_zopen.materialize(a[0], tmp), True)
P = m.frames(rs64_zopen.materialize(a[1], tmp), '--p-retail' in a)   # --p-retail: second capture is a retail-format rdplog too
s14 = lambda v: (v & 0x3FFF) - (0x4000 if v & 0x2000 else 0)
s32 = lambda v: v - (1 << 32) if v & 0x80000000 else v
def tris(F, b0, b1, dyq=0):
    out = []
    for c, _ in F[b0:b1]:
        for k in c:
            if k[0] != 'tri' or len(k) < 10: continue
            w0, w1, xl, dxl, xh, dxh, xm, dxm = k[2:10]
            yl, ym, yh = s14(w0), s14(w1 >> 16), s14(w1)
            out.append(((k[1], (w0 >> 23) & 1, dxl, dxh, dxm, ym - yh, yl - yh), yh + dyq, s32(xh) / 65536.0, s32(dxh) / 65536.0))
    return out
def census(RT, PT):
    idx = collections.defaultdict(list)
    for key, yh, xh, dxh in PT: idx[key].append((yh, xh, dxh))
    dy = collections.Counter(); dyx = collections.Counter(); nk = 0
    for key, yh, xh, dxh in RT:
        ps = idx.get(key)
        if not ps: continue
        nk += 1
        for pyh, pxh, _ in ps[:64]:
            d = pyh - yh; dy[d] += 1
            # XH is the H-edge x at scanline floor(YH): bring both to the retail scanline before comparing
            px_at = pxh + dxh * ((yh >> 2) - (pyh >> 2))
            if abs(px_at - xh) < 0.26: dyx[d] += 1
    return nk, dy, dyx
def show(lab, res):
    nk, dy, dyx = res
    top = dyx.most_common(6)
    print('%-8s shape-matched retail tris %6d | dy (quanta) with XH-consistent pos: %s | all-dy top %s' % (lab, nk, top, dy.most_common(4)))
    return top[0][0] if top else None
RT = tris(R, r0, r1); PT = tris(P, p0, p1)
print('retail tris %d in R[%d:%d], port tris %d in P[%d:%d]' % (len(RT), r0, r1, len(PT), p0, p1))
mode = show('port', census(RT, PT))
rc = 0
if '--controls' in a:
    A = show('ctlA=0', census(RT, RT)); B = show('ctlB+2', census(RT, tris(R, r0, r1, 2)))
    ok = A == 0 and B == 2
    print('controls %s (A mode %s, B mode %s)' % ('PASS' if ok else 'FAIL', A, B)); rc = 0 if ok else 3
POSE = None
print('VERDICT: world-tri dy mode = %s quanta (+2 = 0.5 px lower like the reticle -> H-vp; 0 -> world exact, reticle-only)' % mode)

if '--pose' in a:
    import math
    (q0, q1), (o0, o1) = [tuple(int(v) for v in s.split(':')) for s in a[a.index('--pose') + 1].split(',')]
    XC, YC = 256.0, 224.0   # flight scissor 512x448 centre (s7827: identical scissor/colour image in both arms)
    def static(F, b0, b1):
        cnt = collections.Counter()
        for c, _ in F[b0:b1]:
            for k in set(c):
                if k[0] == 'tri' and len(k) >= 10: cnt[k] += 1
        out = []
        for k, n in cnt.items():
            if n >= 0.9 * (b1 - b0):
                w0, w1, xl, dxl, xh, dxh = k[2:8]
                yh = s14(w1) / 4; ym = s14(w1 >> 16) / 4; yl = s14(w0) / 4
                xt = s32(xh) / 65536 + s32(dxh) / 65536 * (yh - math.floor(yh))
                out.append((k[1], xt, yh, ym, yl))
        return sorted(out)
    SR, SP = static(R, q0, q1), static(P, o0, o1)
    def pair(A, B):
        used, rows = set(), []
        for r in A:
            best = None
            for j, p in enumerate(B):
                if p[0] != r[0] or j in used: continue
                d = abs(p[2] - r[2]) + abs(p[4] - r[4]) + 0.5 * abs(p[1] - r[1])
                if best is None or d < best[0]: best = (d, j, p)
            if best and best[0] < 6: used.add(best[1]); rows.append((r, best[2]))
        return rows
    def pitch(x, y, f, d):
        u, v = (x - XC) / f, (y - YC) / f; z = math.cos(d) - v * math.sin(d)
        return XC + f * u / z, YC + f * (v * math.cos(d) + math.sin(d)) / z
    def obs(rows):   # (x, y, dx|None, dy) samples: top vertex gives x and y, ym/yl give y only
        s = []
        for r, p in rows:
            s.append((r[1], r[2], p[1] - r[1], p[2] - r[2]))
            s.append((r[1], r[3], None, p[3] - r[3])); s.append((r[1], r[4], None, p[4] - r[4]))
        return s
    def rms(s, pred):
        e = []
        for x, y, dx, dy in s:
            px, py = pred(x, y)
            e.append((py - dy) ** 2)
            if dx is not None and abs(x - XC) < 600: e.append((px - dx) ** 2)
        return math.sqrt(sum(e) / len(e))
    def fit(s):
        res = {}
        best = min((rms(s, lambda x, y, c=c: (0.0, c)), c) for c in [i / 100 for i in range(-200, 201)])
        res['H-vp'] = (best[0], 'dy=%+.2f' % best[1])
        best = min((rms(s, lambda x, y, k=k: ((x - XC) * k, (y - YC) * k)), k) for k in [i / 20000 for i in range(-200, 201)])
        res['H-scale'] = (best[0], 'k=%+.4f' % best[1])
        best = min((rms(s, lambda x, y, f=f, d=d: tuple(q - o for q, o in zip(pitch(x, y, f, d), (x, y)))), f, d)
                   for f in range(300, 1001, 20) for d in [i / 20000 for i in range(-80, 81)])
        res['H-pitch'] = (best[0], 'f=%d d=%+.5f rad (%.3f deg)' % (best[1], best[2], math.degrees(best[2])))
        win = min(res, key=lambda k: res[k][0])
        return win, res
    def plant(rows, fn):
        q = lambda v: round(v * 4) / 4
        out = []
        for r, _ in rows:
            xt, yh = fn(r[1], r[2]); _, ym = fn(r[1], r[3]); _, yl = fn(r[1], r[4])
            out.append((r, (r[0], xt, q(yh), q(ym), q(yl))))
        return out
    rows = pair(SR, SP)
    print('pose: static tris R[%d:%d] %d, P[%d:%d] %d, paired %d' % (q0, q1, len(SR), o0, o1, len(SP), len(rows)))
    if not rows:   # s7828: a window whose camera still moves has no static set; say so instead of ZeroDivisionError
        print('pose: NO paired static tris (camera not steady in one of the windows); pick later windows'); sys.exit(2)
    if '--pairs' in a:   # s7828: raw paired static-vertex offsets (top vertex x,y -> dx,dy; ym/yl dy)
        for r, p in sorted(rows, key=lambda rp: rp[0][2]):
            print('  pair x %8.2f y %8.2f  dx %+6.2f dyh %+6.2f dym %+6.2f dyl %+6.2f' % (r[1], r[2], p[1]-r[1], p[2]-r[2], p[3]-r[3], p[4]-r[4]))
    win, res = fit(obs(rows))
    for k, v in sorted(res.items(), key=lambda kv: kv[1][0]): print('  port  %-8s rms %.3f px  %s' % (k, v[0], v[1]))
    POSE = win
    cw1, r1_ = fit(obs(plant(rows, lambda x, y: pitch(x, y, 500, 0.0015))))
    cw2, r2_ = fit(obs(plant(rows, lambda x, y: (x, y + 0.5))))
    print('  ctl pitch(f500,d+0.0015) -> %s %s | ctl const+0.5 -> %s %s' % (cw1, r1_[cw1][1], cw2, r2_[cw2][1]))
    okp = cw1 == 'H-pitch' and cw2 == 'H-vp'
    print('pose controls %s; VERDICT pose: %s' % ('PASS' if okp else 'FAIL', win))
    if not okp: rc = 3
sys.exit(rc)
