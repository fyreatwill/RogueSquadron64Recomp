#!/usr/bin/env python3
"""s7114 fps60-wall-lod: exact drawn-vs-collision terrain height from the bytes both sides read (no clip-space rebuild).

usage: s7114_hsrc.py push.txt [tri.bin tris.bin losscan.txt]   (CHASE file with ROGUESQ_S7114_HSRC=1 hx/ht lines; the optional
       s7112-style captures add the s7113 clip-space rebuild for a bias check against the exact answer)

hx (y-clamp sampler 0x80067D90 under the camera): tile ptr, quarter qx/qz, fractions fx/fz, h, sc, y0, 25 tile bytes.
ht (eye cell TriGen at emit): 10 cmd words, 25 bytes at params[2].
Collision (static read, apply_s7114_hsrc.py): plane A (fx >= fz) h01 + (1-fx)(h00-h01) + fz(h11-h01); plane B h10 + fx(h11-h10)
  + (1-fz)(h00-h10); y = that * sc / 256 + y0 (C = 1/256 checked by control 1).
Drawn (GLideN64 F5Rogue.cpp): lod 0 TriGen0000 = 5x5 nodes, quads split on the same 00-11 diagonal (default order {0,6,1},{0,5,6});
  lod 1 TriGen0001 = nodes 0,2,4 only, 1 u quads split 00-11 ({0,3,4},{0,4,1}); lod 2 flat path = 4 corners, view-dependent diagonal
  (both reported). Ponderation shorts params[5..7] and option bytes params[1] move edge vertices: counted, applied for lod 0/1 edge nodes.
Controls: (1) collision rebuild from b/q/fr/sc/y0 must equal the logged h; (2) ht params[2] must equal hx tl + 5 on ticks where the
camera's tile is the eye cell, and the 25 bytes must match; mismatching ticks are reported, not used."""
import sys, re, bisect, math, collections, runpy
pushf = sys.argv[1]
kv = re.compile(r'(\w+)=(\S+)')
HX = []; HT = []
for line in open(pushf, errors='replace'):
    if line.startswith('hx '):
        d = dict(kv.findall(line))
        if d['tl'] == '00000000' or 'E' in d['b'].upper()[:0]: HX.append(None); continue
        q = [int(x) for x in d['q'].split(',')]; fr = [float(x) for x in d['fr'].split(',')]
        b = bytes.fromhex(d['b']); b = [x - 256 if x > 127 else x for x in b]
        HX.append(dict(m=int(d['m']), tl=int(d['tl'], 16), qx=q[0], qz=q[1], pl=q[2], fx=fr[0], fz=fr[1], h=float(d['h']),
                       sc=float(d['sc']), y0=float(d['y0']), b=b))
    elif line.startswith('ht '):
        d = dict(kv.findall(line)); c = [int(x, 16) for x in d['c'].split(',')]
        b = bytes.fromhex(d['hb']); b = [x - 256 if x > 127 else x for x in b]
        HT.append((int(d['m']), c, b))
HX = [x for x in HX if x]
HT.sort(key=lambda x: x[0]); htm = [x[0] for x in HT]
print(f'hx {len(HX)} (tile found), ht {len(HT)}')

def coll(b, qx, qz, fx, fz):
    v = qz * 5 + qx; h00, h01, h10, h11 = b[v], b[v + 1], b[v + 5], b[v + 6]
    if fx - fz >= 0: return h01 + (1 - fx) * (h00 - h01) + fz * (h11 - h01)
    return h10 + fx * (h11 - h10) + (1 - fz) * (h00 - h10)

def tri_interp(p, a, b_, c):  # barycentric height on triangle of (x, z, h); None if outside
    (x, z) = p; (x1, z1, h1), (x2, z2, h2), (x3, z3, h3) = a, b_, c
    den = (z2 - z3) * (x1 - x3) + (x3 - x2) * (z1 - z3)
    if abs(den) < 1e-12: return None
    l1 = ((z2 - z3) * (x - x3) + (x3 - x2) * (z - z3)) / den; l2 = ((z3 - z1) * (x - x3) + (x1 - x3) * (z - z3)) / den; l3 = 1 - l1 - l2
    if min(l1, l2, l3) < -1e-9: return None
    return l1 * h1 + l2 * h2 + l3 * h3

def drawn(b, lod, X, Z, diag=0):  # X, Z in cell node units 0..4
    if lod == 0:
        qx, qz = min(int(X), 3), min(int(Z), 3); fx, fz = X - qx, Z - qz
        return coll(b, qx, qz, fx, fz)  # same nodes, same diagonal
    if lod == 1:
        qx, qz = min(int(X / 2), 1), min(int(Z / 2), 1); fx, fz = X / 2 - qx, Z / 2 - qz
        n = lambda i, j: b[(2 * (qz + j)) * 5 + 2 * (qx + i)]
        h00, h01, h10, h11 = n(0, 0), n(1, 0), n(0, 1), n(1, 1)  # h01 = x+1, h10 = z+1 (sampler naming)
        if fx - fz >= 0: return h01 + (1 - fx) * (h00 - h01) + fz * (h11 - h01)
        return h10 + fx * (h11 - h10) + (1 - fz) * (h00 - h10)
    if lod == 2:
        fx, fz = X / 4, Z / 4; h00, h01, h10, h11 = b[0], b[4], b[20], b[24]
        if diag == 0:
            if fx - fz >= 0: return h01 + (1 - fx) * (h00 - h01) + fz * (h11 - h01)
            return h10 + fx * (h11 - h10) + (1 - fz) * (h00 - h10)
        if fx + fz <= 1: return h00 + fx * (h01 - h00) + fz * (h10 - h00)
        return h11 + (1 - fx) * (h10 - h11) + (1 - fz) * (h01 - h11)
    return None

# ---- control 1: collision rebuild == logged h
c1 = []
for x in HX:
    hc = coll(x['b'], x['qx'], x['qz'], x['fx'], x['fz']) * x['sc'] / 256.0 + x['y0']
    c1.append(abs(hc - x['h']))
c1.sort(); n = len(c1)
print(f'CONTROL 1 collision rebuild vs logged h: n {n} |err| p50 {c1[n // 2]:.2e} p99 {c1[int(0.99 * (n - 1))]:.2e} max {c1[-1]:.2e} '
      f'exact(<1e-4) {sum(1 for e in c1 if e < 1e-4) / n:.4f}')
# plane control: the logged plane bit vs fx >= fz
print('CONTROL 1b plane bit agrees with fx-fz sign:', sum(1 for x in HX if (x['pl'] == 0) == (x['fx'] - x['fz'] >= 0)), '/', len(HX))

# ---- join each hx with the first eye-cell TriGen emitted after it (the render of this tick)
# command class: mode = (w0 >> 8) & 0xFF; mode 2/3 = flat 4-corner path (heights inline: c[1] = b0<<20 | b4<<4, c[2] = b20<<20 | b24<<4);
# mode 0: lod = w0 & 0xFF (0 = TriGen0000, 1 = TriGen0001), params[2] = height pointer.
OPT0 = {0x0000FF00: (0x00000100, [(0, 2, 1), (2, 4, 3)]), 0x000000FF: (0x00000001, [(20, 22, 21), (22, 24, 23)]),
        0xFF000000: (0x01000000, [(0, 10, 5), (10, 20, 15)]), 0x00FF0000: (0x00010000, [(4, 14, 9), (14, 24, 19)])}
def corrected0(b, opt):  # TriGen0000 options (GLideN64 vtx index ^ 1 = byte index): edge mid-nodes set to the mean of their neighbours
    v = [x << 4 for x in b]
    for msk, (val, ops) in OPT0.items():
        if opt & msk == val:
            for s1, s2, d in ops: v[d] = int((v[s1] + v[s2]) / 2)  # C s16 division truncates toward 0
    return [x / 16.0 for x in v]
J = []; cnt = collections.Counter(); bytes_eq = 0
for x in HX:
    k = bisect.bisect_left(htm, x['m'])
    if k >= len(HT) or HT[k][0] - x['m'] > 40 * 24000: cnt['no ht within 40 ms'] += 1; continue
    m, c, hb = HT[k]; mode = (c[0] >> 8) & 0xFF; lod = c[0] & 0xFF
    if mode in (2, 3):
        sx = lambda w: ((w >> 20) - 4096 if (w >> 20) > 2047 else (w >> 20)) / 1.0
        cor = [((c[1] >> 24) - 256 if (c[1] >> 24) > 127 else c[1] >> 24), ]
        b0 = (c[1] >> 20) & 0xFFF; b0 = b0 - 4096 if b0 > 2047 else b0
        b4 = (c[1] & 0xFFFF) >> 4; b4 = b4 - 4096 if b4 > 2047 else b4
        b20 = (c[2] >> 20) & 0xFFF; b20 = b20 - 4096 if b20 > 2047 else b20
        b24 = (c[2] & 0xFFFF) >> 4; b24 = b24 - 4096 if b24 > 2047 else b24
        ok = [b0, b4, b20, b24] == [x['b'][0], x['b'][4], x['b'][20], x['b'][24]]
        cnt['flat, corners == camera tile' if ok else 'flat, other cell'] += 1
        if ok: J.append((x, 'flat', c, x['b'], (b0, b4, b20, b24)))
        continue
    p2 = 0x80000000 | (c[2] & 0xFFFFFF)
    if p2 != x['tl'] + 5: cnt['mode0, other cell'] += 1; continue
    bytes_eq += hb == x['b']
    pond = (c[5] & 0xFFFF, c[5] >> 16, c[6] & 0xFFFF, c[6] >> 16, c[7] >> 16)
    if any(pond): cls = f'lod{lod} ponderation'
    elif lod == 0: cls = 'lod0 opt' if any(c[1] & msk == val for msk, (val, _) in OPT0.items()) else 'lod0 plain'
    elif lod == 1: cls = 'lod1 opt' if any(((c[1] >> s) & 0xFF) == 2 for s in (0, 8, 16, 24)) else 'lod1 plain'
    else: cls = f'lod{lod}?'
    cnt[cls] += 1; J.append((x, cls, c, hb, None))
print(f'CONTROL 2 join (eye-cell TriGen source == camera tile): {dict(cnt)}; pointer-joined bytes identical {bytes_eq}')

def q(v, qs=(0.1, 0.25, 0.5, 0.75, 0.9)):
    v = sorted(v); n = len(v)
    return '/'.join('%+.4f' % v[int(t * (n - 1))] for t in qs) if n else '-'
def surf(cls, c, hb, X, Z, diag=0):
    if cls == 'lod0 plain': return drawn(hb, 0, X, Z)
    if cls == 'lod0 opt': return drawn(corrected0(hb, c[1]), 0, X, Z)
    if cls == 'lod1 plain': return drawn(hb, 1, X, Z)
    if cls == 'flat': return drawn(hb, 2, X, Z, diag)
    return None
print('\nEXACT drawn minus collision height (world u = s8 * sc / 256; + = drawn larger y = lower in the y-down world):')
D = collections.defaultdict(list); DA = collections.defaultdict(list); XDRAW = {}
for x, cls, c, hb, _ in J:
    X, Z = x['qx'] + x['fx'], x['qz'] + x['fz']; s = x['sc'] / 256.0
    hc = coll(hb, x['qx'], x['qz'], x['fx'], x['fz'])
    for dg in ((0, 1) if cls == 'flat' else (0,)):
        h = surf(cls, c, hb, X, Z, dg)
        if h is None: continue
        key = cls + ('' if cls != 'flat' else ' diag%d' % dg); D[key].append((h - hc) * s)
        if dg == 0: XDRAW[x['m']] = ((h - hc) * s, cls)
        mx = 0
        for gi in range(17):
            for gj in range(17):
                Xg, Zg = gi / 4, gj / 4; qx, qz = min(int(Xg), 3), min(int(Zg), 3)
                mx = max(mx, abs(surf(cls, c, hb, Xg, Zg, dg) - coll(hb, qx, qz, Xg - qx, Zg - qz)))
        DA[key].append(mx * s)
for k in sorted(D):
    v = D[k]; print(f'  {k:18s} n {len(v):5d} under camera p10/p25/p50/p75/p90 {q(v)}  |d|<0.01 {sum(1 for a in v if abs(a) < 0.01) / len(v):.3f}'
                    f'  |d|>0.05 {sum(1 for a in v if abs(a) > 0.05) / len(v):.3f} | cell max |d| p50/p90/max {q(DA[k], (0.5, 0.9, 1.0))}')

# ---- optional: s7113 clip-space rebuild on the same capture, error vs the exact answer
if len(sys.argv) >= 5:
    sys.argv = [sys.argv[0], sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4]]  # s7113 order: tri push tris losscan
    G = runpy.run_path(str(__import__('pathlib').Path(__file__).with_name('s7113_raymiss.py')), run_name='s7113')  # noqa
    A, SWM, flight, tick = G['A'], G['SWM'], G['flight'], G['tick']
    loss = set(G['loss'])
    byM = sorted((x['m'], i) for i, (x, *_r) in enumerate(J)); bm = [a for a, _ in byM]
    E = collections.defaultdict(list); EL = collections.defaultdict(list)
    for sw in flight:
        a = A.get(sw)
        if not a or not a['rxd']: continue
        t = tick(sw); m = t['m']
        i = bisect.bisect_left(bm, m)
        if i >= len(bm) or bm[i] - m > 40 * 24000: continue
        x, lod, c, hb, _ = J[byM[i][1]]
        X, Z = x['qx'] + x['fx'], x['qz'] + x['fz']; s = x['sc'] / 256.0
        h = surf(lod, c, hb, X, Z)
        if h is None: continue
        ex = (h - coll(hb, x['qx'], x['qz'], x['fx'], x['fz'])) * s
        E[lod].append(a['rxd'][0] - ex)
        if sw in loss: EL[lod].append((a['rxd'][0], ex))
    print('\nREBUILD BIAS (s7113 clip-space drawn-minus-h minus the exact drawn-minus-h, same tick):')
    for k in sorted(E): print(f'  lod {k}: n {len(E[k])} p10/p25/p50/p75/p90 {q(E[k])}')
    for k in sorted(EL): print(f'  loss lod {k}: (rebuilt, exact) ' + ' '.join('(%+.3f,%+.3f)' % p for p in EL[k][:40]))
    # loss swaps by eye-cell command class (exact join), vs all flight swaps
    CL = collections.Counter(); CA = collections.Counter(); LM = []
    for sw in flight:
        t = tick(sw)
        if not t: continue
        i = bisect.bisect_left(bm, t['m'])
        if i >= len(bm) or bm[i] - t['m'] > 40 * 24000: cls = 'no join'
        else:
            x, cls, c, hb, _ = J[byM[i][1]]
            if sw in loss:
                mx = 0
                for gi in range(17):
                    for gj in range(17):
                        Xg, Zg = gi / 4, gj / 4; qx, qz = min(int(Xg), 3), min(int(Zg), 3); h = surf(cls, c, hb, Xg, Zg)
                        if h is not None: mx = max(mx, abs(h - coll(hb, qx, qz, Xg - qx, Zg - qz)))
                LM.append((sw, cls, round(mx * x['sc'] / 256.0, 3)))
        CA[cls] += 1
        if sw in loss: CL[cls] += 1
    print('\nLOSS CLASS (eye-cell command class on loss swaps vs all flight swaps):')
    for k in sorted(CA): print(f'  {k:18s} flight {CA[k]:5d} ({CA[k] / sum(CA.values()):.3f})  loss {CL[k]:3d} ({CL[k] / max(sum(CL.values()), 1):.3f})')
    print('  loss swaps (sw, class, eye-cell max |drawn - collision|):', LM)
