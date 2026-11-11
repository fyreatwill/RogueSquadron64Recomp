#!/usr/bin/env python3
"""s7112 fps60-wall-reject: does the F5 ucode drop eye-cell triangles that are visible?

Input: ROGUESQ_S7112_TRI binary (src/rsp/s7106_rsptri.cpp rs64_s7112_tri), 136 B records: u32 magic, u32 sw, u32 w0,
u16 cmd ordinal, u8 tag (24 = eye cell, 0xFE eye by near key, 0x80|cls = 1/64 control sample), u8 nrdp (RDP tris the source
triangle produced, DMEM parse), 3 x 0x28 B vertex records (RSP byte order): +0 clip x,y,z,w s16 int, +8 x,y,z,w u16 frac,
+0x18 screen x,y (s13.2), +0x24 clip flags (0x7070 frustum LE/GE x,y,z; 0x0707 guard band).

Offline exact reference: clip the homogeneous triangle against -w<=x<=w, -w<=y<=w, -w<=z<=w (Sutherland-Hodgman in 4D), project
the surviving polygon, signed NDC area. A triangle with visible area > A_MIN that the ucode turns into 0 RDP tris, with the
facing that the control population shows is drawn, is a REJECTED-VISIBLE triangle (H-reject). If every visible eye-cell tri is
emitted, the near cut is correct clipping (the wall really lies between the eye and the near plane: H-raymiss / geometry).

usage: s7112_trireject.py tri.bin [losscan.txt] [A_MIN=0.002]
"""
import sys, struct
from collections import Counter, defaultdict

path = sys.argv[1]
loss = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].replace('.', '').isdigit() else None
AMIN = float(sys.argv[-1]) if sys.argv[-1].replace('.', '').isdigit() else 0.002
data = open(path, 'rb').read()
R = 136
n = len(data) // R


def vtx(b):
    xi, yi, zi, wi = struct.unpack('>4h', b[0:8]); xf, yf, zf, wf = struct.unpack('>4H', b[8:16])
    sx, sy = struct.unpack('>2h', b[0x18:0x1C]); fl, = struct.unpack('>H', b[0x24:0x26])
    return (xi + xf / 65536.0, yi + yf / 65536.0, zi + zf / 65536.0, wi + wf / 65536.0), (sx / 4.0, sy / 4.0), fl


PLANES = [(1, 0, 0, 1), (-1, 0, 0, 1), (0, 1, 0, 1), (0, -1, 0, 1), (0, 0, 1, 1), (0, 0, -1, 1)]  # dot >= 0 is inside


def clip(poly, planes):
    for p in planes:
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            da = sum(p[k] * a[k] for k in range(4)); db = sum(p[k] * b[k] for k in range(4))
            if da >= 0: out.append(a)
            if (da >= 0) != (db >= 0):
                t = da / (da - db); out.append(tuple(a[k] + t * (b[k] - a[k]) for k in range(4)))
        poly = out
        if not poly: return []
    return poly


def sarea(poly):
    pts = [(v[0] / v[3], v[1] / v[3]) for v in poly if v[3] > 1e-9]
    if len(pts) < 3: return 0.0
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]; s += x0 * y1 - x1 * y0
    return s / 2.0 / 4.0  # fraction of the viewport (NDC square area 4), signed


def klass(fl):
    a = fl[0] & fl[1] & fl[2] & 0x7070
    if a: return 'tclip'
    if (fl[0] | fl[1] | fl[2]) & 0x4343: return 'hand'
    return 'setup'


recs = []
bad = 0
for i in range(n):
    b = data[i * R:(i + 1) * R]
    mg, sw, w0, ordn, tag, nrdp = struct.unpack('<IIIHBB', b[:16])
    if mg != 0x37313132: bad += 1; continue
    vs = [vtx(b[16 + k * 0x28:16 + (k + 1) * 0x28]) for k in range(3)]
    c4 = [v[0] for v in vs]; fl = [v[2] for v in vs]
    poly = clip(c4, PLANES)
    a = sarea(poly)
    nearpart = sum(1 for v in c4 if v[2] < -v[3])  # vertices outside the near plane (z < -w)
    behind = sum(1 for v in c4 if v[3] <= 0)
    recs.append(dict(sw=sw, w0=w0, ordn=ordn, tag=tag, nrdp=nrdp, k=klass(fl), a=a, np=nearpart, bh=behind, fl=fl, c4=c4))
print(f'records {len(recs)} bad magic {bad}')
eye = [r for r in recs if r['tag'] in (24, 0xFE)]
ctl = [r for r in recs if r['tag'] & 0x80 and r['tag'] != 0xFE]
print(f'eye-cell tris {len(eye)} over {len(set(r["sw"] for r in eye))} swaps; control samples {len(ctl)}')


def table(name, rs):
    print(f'--- {name}: class x (visible?, sign) -> emitted 0 / >=1')
    t = defaultdict(lambda: [0, 0])
    for r in rs:
        vis = 'vis' if abs(r['a']) > AMIN else ('tiny' if abs(r['a']) > 0 else 'none')
        sg = '+' if r['a'] > 0 else '-' if r['a'] < 0 else '0'
        t[(r['k'], vis, sg)][1 if r['nrdp'] else 0] += 1
    for key in sorted(t): print(f'  {key[0]:5s} {key[1]:4s} {key[2]}  emit0 {t[key][0]:7d}  emit>=1 {t[key][1]:7d}')


table('control (1/64 of all TRI_GEN tris)', ctl)
table('eye cell', eye)
# facing learned from the control: which sign of visible area is emitted on the setup path
ce = Counter((r['a'] > 0, r['nrdp'] > 0) for r in ctl + eye if r['k'] == 'setup' and abs(r['a']) > AMIN)
print('setup-path visible: (area>0, emitted) counts', dict(ce))
front_pos = ce[(True, True)] >= ce[(False, True)]
print('front-facing sign (learned):', '+' if front_pos else '-')
fr = lambda r: (r['a'] > 0) == front_pos and abs(r['a']) > AMIN
rv = [r for r in eye if fr(r) and r['nrdp'] == 0]
print(f'EYE REJECTED-VISIBLE (front, area>{AMIN}, 0 RDP tris): {len(rv)} of {sum(1 for r in eye if fr(r))} front-visible eye tris')
print('  by class', Counter(r['k'] for r in rv), ' near-outside vertex count', Counter(r['np'] for r in rv), ' w<=0 count', Counter(r['bh'] for r in rv))
rvc = [r for r in ctl if fr(r) and r['nrdp'] == 0]
print(f'CONTROL rejected-visible: {len(rvc)} of {sum(1 for r in ctl if fr(r))}')
for r in sorted(rv, key=lambda r: -abs(r['a']))[:8]:
    print(f"  sw {r['sw']} ord {r['ordn']} {r['k']} a={r['a']:+.3f} fl={['%04x' % f for f in r['fl']]} "
          f"c4={[tuple(round(c, 1) for c in v) for v in r['c4']]}")
# near-crossing eye tris: what the ucode does with them
nc = [r for r in eye if 0 < r['np'] < 3]
print(f'eye near-crossing tris {len(nc)}: emitted dist', Counter(min(r['nrdp'], 4) for r in nc),
      ' class', Counter(r['k'] for r in nc), ' front-visible', sum(1 for r in nc if fr(r)),
      ' front-visible emit0', sum(1 for r in nc if fr(r) and r['nrdp'] == 0))
if loss:
    import re
    rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
    ls = set()
    for l in open(loss):  # s7108_split eye-cell near-z loss: ref painter's top cell c+0+0 and drop near minz < 0x100
        g = rl.search(l)
        if g and "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100: ls.add(int(g.group(1)))
    by = defaultdict(list)
    for r in eye: by[r['sw']].append(r)
    for lag in (-2, -1, 0, 1, 2):
        hit = [s + lag for s in ls if s + lag in by]
        tot = sum(len(by[s]) for s in hit); rej = sum(1 for s in hit for r in by[s] if fr(r) and r['nrdp'] == 0)
        vis = sum(1 for s in hit for r in by[s] if fr(r))
        print(f'loss swaps lag {lag:+d}: {len(hit)}/{len(ls)} have eye records, tris {tot}, front-visible {vis}, rejected-visible {rej}')
