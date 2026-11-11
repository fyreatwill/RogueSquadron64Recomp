#!/usr/bin/env python3
"""s7113 fps60-wall-raymiss: is the surface the camera push-out probes the same surface the eye-cell TRI_GEN mesh renders?

Offline, capture once: one s7112 run (ROGUESQ_S7112_TRI records + ROGUESQ_S7101_CHASE log + G5B_TRIS swap clock + s7107 losscan).
Reconstruction (no new build): the s7112 records hold every eye-cell source triangle in clip space (s16.16). From the data:
  * clip z = 1.0018 w - 60.05 on eye vertices (residual p50 0.05), so z = -w at w_n = 30.0; with near = f20 / 2 = 0.1172 game
    units, w = 256 * eye depth (game units).
  * x = 256 P00 xe, y = 256 P11 ye; P00 / P11 fitted below by snapping rebuilt vertices to the TriGen quarter-cell lattice
    (0.5 world units): the positive control for the whole chain (basis, eye, timing, P).
  * camera basis = the push-out corner frame of the same tick (CHASE pu lines: corners c - pre are (+-0.164, +-0.092, 0.140) in
    an orthonormal r/u/f frame), eye = bv rd (terrain builder eye = pushed pos, s7111), tick = last bv before the swap's mach.
Per swap (eye records, tick dt < 40 ms):
  rays  : the 4 push corner segments (3 retail-tested + corner 3) from the RENDER eye (pushed pos), in view space; first
          crossing parameter t (0..1 of f20) with the rendered eye-cell triangles.
  near  : the part of each eye-cell tri inside the in-view near pyramid (0 < w, |x|,|y| <= w, z < -w), as a fraction of the near
          rectangle (what the ucode must cut away -> the s7107 straight cut).
  world : positive control for surface identity: on pu hit corners (pre -> c, retail ray), the rebuilt eye-cell surface crossing
          vs the game's hit point hp.
Groups: eye-cell near-z loss swaps (s7108 criterion: ref painter top cell c+0+0 and drop near minz < 0x100), all flight swaps,
and the loss times shifted +-3 s.
Outcomes: rays crossed by the rendered tris on loss swaps while the collision called the same rays clear -> H-lod / H-space
(collision != render surface); rendered tris inside the near pyramid with all 4 rays uncrossed -> H-gap (the wall enters between
the rays, the probe pattern cannot see it).
usage: s7113_raymiss.py tri.bin push.txt tris.bin losscan.txt [P00 P11]"""
import sys, struct, re, math, mmap, bisect, random
from collections import Counter, defaultdict

trib, pushf, trisb, lsc = sys.argv[1:5]
FIT = len(sys.argv) <= 5
P00, P11 = (float(sys.argv[5]), float(sys.argv[6])) if not FIT else (0.72, 1.54)
FC = '80138458'
sub = lambda a, b: [x - y for x, y in zip(a, b)]
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def nrm(a):
    l = math.sqrt(dot(a, a)); return [x / l for x in a]

# ---- eye-cell source triangles (s7112 records)
R = 136
data = open(trib, 'rb').read()
eye = defaultdict(list)
for i in range(len(data) // R):
    b = data[i * R:(i + 1) * R]
    mg, sw, w0, ordn, tag, nrdp = struct.unpack('<IIIHBB', b[:16])
    if mg != 0x37313132 or tag not in (24, 0xFE): continue
    vs = []
    for k in range(3):
        v = b[16 + k * 0x28:16 + (k + 1) * 0x28]
        xi, yi, zi, wi = struct.unpack('>4h', v[0:8]); xf, yf, zf, wf = struct.unpack('>4H', v[8:16])
        vs.append((xi + xf / 65536.0, yi + yf / 65536.0, zi + zf / 65536.0, wi + wf / 65536.0))
    eye[sw].append((nrdp, vs))
del data
# ---- swap clock (G5B_TRIS markers)
F = open(trisb, 'rb'); d = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ)
M = b'\xf5\xf5\xf5\xf5'; SWM = {}; p = d.find(M)
while p >= 0:
    n = d.find(M, p + 16)
    while n > 0 and (n - p - 16) % 32: n = d.find(M, n + 1)
    t, q = struct.unpack_from('<QI', d, p + 4); SWM[q] = t; p = n
# ---- CHASE ticks of the flight camera
kv = re.compile(r'(\w+)=(\S+)'); V = lambda s: [float(x) for x in s.split(',')]
T = []; cur = None
for line in open(pushf, errors='replace'):
    k = line[:2]
    if k not in ('ch', 'pu', 'pe', 'bv', 'rx', 'pc'): continue
    dd = dict(kv.findall(line))
    if dd.get('cam') != FC: continue
    if k == 'ch': cur = {'m': int(dd['m']), 'pu': [], 'bv': None, 'rx': None, 'pc': None}; T.append(cur)
    elif cur is None: continue
    elif k == 'pu': cur['pu'].append((int(dd['i']), int(dd['hit']), V(dd['c']), V(dd['pre']), V(dd['hp']), float(dd['f20'])))
    elif k == 'bv': cur['bv'] = (int(dd['m']), V(dd['rd']))
    elif k == 'rx': cur['rx'] = (V(dd['o']), float(dd['h'])); cur['rmask'] = int(dd['r'])  # y-clamp terrain height sample at (o.x, o.z)
    elif k == 'pc': cur['pc'] = (int(dd['hit']), V(dd['c']), V(dd['pos']))  # corner 3 re-test from the final pos
def basis(t):
    pu = [x for x in t['pu'] if x[0] in (0, 1, 2)][:3]
    if len(pu) < 3 or [x[0] for x in pu] != [0, 1, 2]: return None
    o = [sub(x[2], pu[0][3]) for x in pu]  # corners are built from the loop-start pos p0 (= corner 0's pre), s7103
    r = nrm(sub(o[1], o[0])); u = nrm(sub(o[2], o[1])); f = nrm(cross(r, u))
    if dot(o[0], f) < 0: f = [-x for x in f]
    ov = [(dot(x, r), dot(x, u), dot(x, f)) for x in o]
    ov.append((ov[0][0], ov[2][1], ov[0][2]))  # corner 3 (retail does not ray-test it)
    return r, u, f, ov, pu[0][5]
TB = []
for t in T:
    if t['bv']:
        bs = basis(t)
        if bs: t['bs'] = bs; TB.append(t)
bm = [t['bv'][0] for t in TB]
def tick(sw):
    m = SWM.get(sw)
    if m is None: return None
    j = bisect.bisect_left(bm, m) - 1
    if j < 0 or m - bm[j] > 40 * 24e3: return None
    return TB[j]
def view(v):  # clip -> view (right, up, depth), game units
    return (v[0] / (256 * P00), v[1] / (256 * P11), v[3] / 256.0)
def world(pv, t):
    r, u, f = t['bs'][:3]; e = t['bv'][1]
    return [e[k] + pv[2] * f[k] + pv[0] * r[k] + pv[1] * u[k] for k in range(3)]
def snap(sws, q=0.5):
    s = n = 0
    for sw in sws:
        t = tick(sw)
        if not t: continue
        for nr, vs in eye[sw]:
            for v in vs:
                if v[3] <= 0: continue
                X = world(view(v), t)
                for c in (X[0], X[2]):
                    fr = (c / q) % 1.0; s += min(fr, 1 - fr); n += 1
    return s / max(n, 1), n

random.seed(7)
flight = [sw for sw in sorted(eye) if tick(sw)]
print(f'eye swaps {len(eye)}, with a flight tick (dt < 40 ms) {len(flight)}; flight ticks {len(T)}, with basis {len(TB)}')
samp = random.sample(flight, min(400, len(flight)))
if FIT:
    grid = []
    for a in [0.66 + 0.01 * i for i in range(13)]:
        for b in [1.44 + 0.02 * i for i in range(11)]:
            P00, P11 = a, b; grid.append((snap(samp)[0], a, b))
    best = min(grid); P00, P11 = best[1], best[2]
s0 = snap(samp)
P00s, P11s = P00, P11
P00, P11 = 0.851, 1.511; sw_ = snap(samp)  # push-corner frustum as P: wrong-P control
P00, P11 = P00s, P11s
print(f'POSITIVE CONTROL lattice snap (0.5 u, random 0.25): P00 {P00:.3f} P11 {P11:.3f} -> {s0[0]:.4f} over {s0[1]} coords; '
      f'push-corner P (0.851/1.511) {sw_[0]:.4f}')

def static_check(lag=0, k=8):
    """terrain is static: the same lattice node rebuilt from two camera poses k swaps apart must coincide"""
    fs = set(flight); dy = []; dh = []; off = []
    def nodes(sw):
        m = SWM[sw]; j = bisect.bisect_left(bm, m) - 1 - lag; t = TB[j]; out = {}
        for nr, vs in eye[sw]:
            for v in vs:
                if v[3] <= 0: continue
                X = world(view(v), t); out[(round(X[0] / 0.5), round(X[2] / 0.5))] = X
        return out
    for a in samp:
        if a + k not in fs: continue
        A_, B_ = nodes(a), nodes(a + k)
        for key in A_.keys() & B_.keys():
            p_, q_ = A_[key], B_[key]; dy.append(abs(p_[1] - q_[1])); dh.append(math.hypot(p_[0] - q_[0], p_[2] - q_[2]))
            off.append(math.hypot(p_[0] - key[0] * 0.5, p_[2] - key[1] * 0.5))
    dy.sort(); dh.sort(); off.sort(); n = len(dy)
    return n, dy[n // 2], dy[(9 * n) // 10], dh[n // 2], dh[(9 * n) // 10], off[n // 2], off[(9 * n) // 10]
for lg in (0, 1):
    r_ = static_check(lg)
    print(f'POSITIVE CONTROL static terrain (lag {lg}): {r_[0]} node pairs 8 swaps apart, |dy| p50/p90 {r_[1]:.4f}/{r_[2]:.4f}, '
          f'|dxz| p50/p90 {r_[3]:.4f}/{r_[4]:.4f}; rendered vertex offset from the 0.5-unit lattice p50/p90 {r_[5]:.4f}/{r_[6]:.4f}')

def seg_tri(o, dvec, a, b, c):  # Moller-Trumbore: param s in [0,1] along o + s*dvec, or None
    e1 = sub(b, a); e2 = sub(c, a); h = cross(dvec, e2); det = dot(e1, h)
    if abs(det) < 1e-12: return None
    inv = 1.0 / det; sv = sub(o, a); uu = dot(sv, h) * inv
    if uu < 0 or uu > 1: return None
    qv = cross(sv, e1); vv = dot(dvec, qv) * inv
    if vv < 0 or uu + vv > 1: return None
    s = dot(e2, qv) * inv
    return s if 0 <= s <= 1 else None

NEARP = [(1, 0, 0, 1), (-1, 0, 0, 1), (0, 1, 0, 1), (0, -1, 0, 1), (0, 0, -1, -1), (0, 0, 0, 1)]  # in view, in front of near
def clip(poly, planes):
    for pl in planes:
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            da = sum(pl[k] * a[k] for k in range(4)); db = sum(pl[k] * b[k] for k in range(4))
            if da >= 0: out.append(a)
            if (da >= 0) != (db >= 0):
                tt = da / (da - db); out.append(tuple(a[k] + tt * (b[k] - a[k]) for k in range(4)))
        poly = out
        if not poly: return []
    return poly
def near_frac(vs):
    """area of the in-near-pyramid part projected through the eye onto the near rectangle, fraction of that rectangle"""
    poly = clip(list(vs), NEARP)
    pts = [(v[0] / v[3], v[1] / v[3]) for v in poly if v[3] > 1e-6]
    if len(pts) < 3: return 0.0
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]; s += x0 * y1 - x1 * y0
    return abs(s) / 2.0 / 4.0

def analyse(sw):
    t = tick(sw)
    r, u, f, ov, f20 = t['bs']
    tris = [(nr, vs, [view(v) for v in vs]) for nr, vs in eye[sw]]
    o = (0.0, 0.0, 0.0)
    ray = []
    for c in ov:
        best = None
        for nr, vs, pv in tris:
            s = seg_tri(o, c, *pv)
            if s is not None and (best is None or s < best): best = s
        ray.append(best)
    nf = sum(near_frac(vs) for nr, vs, pv in tris)
    nfe = sum(near_frac(vs) for nr, vs, pv in tris if nr > 0)  # part of the near region on tris the ucode still emits
    mind = min(min(math.sqrt(dot(p, p)) for p in pv) for nr, vs, pv in tris)
    # world positive control on the retail ray tests of this tick
    wc = []; sg = []
    for i, hit, c, pre, hp, _ in t['pu']:
        if not hit: continue
        dv = sub(c, pre); best = None
        for nr, vs, pv in tris:
            W = [world(p, t) for p in pv]
            s = seg_tri(pre, dv, *W)
            if s is not None and (best is None or s < best): best = s
        if best is not None:
            X = [pre[k] + best * dv[k] for k in range(3)]
            wc.append(math.sqrt(dot(sub(X, hp), sub(X, hp))))
            L = math.sqrt(dot(dv, dv)); sh = math.sqrt(dot(sub(hp, pre), sub(hp, pre)))
            sg.append(best * L - sh)  # signed: < 0 = the rendered surface is nearer the eye than the collision hit
        else: wc.append(None)
    hits = [x[1] for x in t['pu'] if x[0] in (0, 1, 2)][:3]
    W = [[world(p, t) for p in pv] for nr, vs, pv in tris]
    def hgt(x, z):
        best = None
        for w3 in W:
            sv = seg_tri([x, 1e4, z], [0, -2e4, 0], *w3)
            if sv is not None and (best is None or 1e4 - 2e4 * sv > best): best = 1e4 - 2e4 * sv
        return best
    rxd = None
    if t['rx']:
        o_, h_ = t['rx']; hr = hgt(o_[0], o_[2])
        if hr is not None: rxd = (hr - h_, o_)
    pcd = None
    if t['pc']:
        ph, pcc, ppos = t['pc']; dv = sub(pcc, ppos); best = None
        for w3 in W:
            sv = seg_tri(ppos, dv, *w3)
            if sv is not None and (best is None or sv < best): best = sv
        pcd = (ph, best)
    return dict(rmask=t.get('rmask'), rxd=rxd, pcd=pcd, sg=sg, ray=ray, nf=nf, nfe=nfe, mind=mind, wc=wc, hits=hits, f20=f20, nt=len(tris))

# ---- loss swaps
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
loss = []
for line in open(lsc):
    g = rl.search(line)
    if not g or float(g.group(2)) < 0: continue
    if "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100: loss.append(int(g.group(1)))
fl_m = sorted((SWM[s], s) for s in flight)
def shifted(sw, dt):
    m = SWM[sw] + dt * 24e6; j = bisect.bisect_left(fl_m, (m, 0))
    return fl_m[min(j, len(fl_m) - 1)][1] if fl_m else None

A = {sw: analyse(sw) for sw in flight}
def rep(name, sws):
    sws = [s for s in sws if s in A]
    n = len(sws)
    if not n: print(f'{name:28s} n=0'); return
    rc = [sum(1 for s in sws if A[s]['ray'][k] is not None) / n for k in range(4)]
    anyr = sum(1 for s in sws if any(x is not None for x in A[s]['ray'][:3])) / n
    anyr4 = sum(1 for s in sws if any(x is not None for x in A[s]['ray'])) / n
    inn = [s for s in sws if A[s]['nf'] > 0.01]
    gap = sum(1 for s in inn if all(x is None for x in A[s]['ray'])) / max(len(inn), 1)
    nfs = sorted(A[s]['nf'] for s in sws)
    hit = sum(1 for s in sws if any(A[s]['hits'])) / n
    cr_nohit = sum(1 for s in sws if any(A[s]['ray'][k] is not None and not A[s]['hits'][k] for k in range(3))) / n
    md = sorted(A[s]['mind'] for s in sws)
    print(f'{name:28s} n={n:5d} near-frac p50/p90 {nfs[n // 2]:.3f}/{nfs[(9 * n) // 10]:.3f} in-near(>1%) {len(inn) / n:.3f} | '
          f'rendered crosses ray0-3 {rc[0]:.2f} {rc[1]:.2f} {rc[2]:.2f} {rc[3]:.2f} any3 {anyr:.3f} any4 {anyr4:.3f} | '
          f'retail hit {hit:.3f} crossed-but-clear {cr_nohit:.3f} | in-near & no ray {gap:.3f} | min vert dist p50 {md[n // 2]:.3f}')
print(f'loss swaps {len(loss)} (with records/tick {sum(1 for s in loss if s in A)})')
rep('ALL flight swaps', flight)
rep('eye-cell near-z LOSS swaps', loss)
for lag in (-2, -1, 1, 2):
    idx = {sw: i for i, (m, sw) in enumerate(fl_m)}
    rep(f'loss lag {lag:+d} swaps', [fl_m[idx[s] + lag][1] for s in loss if s in idx and 0 <= idx[s] + lag < len(fl_m)])
rep('loss -3 s', [shifted(s, -3) for s in loss if s in SWM])
rep('loss +3 s', [shifted(s, 3) for s in loss if s in SWM])
# world positive control
wc = [x for s in flight for x in A[s]['wc']]
fnd = sorted(x for x in wc if x is not None)
print(f'POSITIVE CONTROL world: retail ray hits {len(wc)}, rebuilt eye-cell surface crosses the same ray on {len(fnd)} '
      f'({len(fnd) / max(len(wc), 1):.3f}); |crossing - hp| p10/p50/p90 ' +
      ('%.4f/%.4f/%.4f' % (fnd[len(fnd) // 10], fnd[len(fnd) // 2], fnd[(9 * len(fnd)) // 10]) if fnd else '-') + ' (f20 0.234)')
def sgrep(name, sws):
    v = sorted(x for s in sws if s in A for x in A[s]['sg'])
    if not v: print(f'SIGNED {name}: n=0'); return
    n = len(v)
    print(f'SIGNED render-minus-collision along retail hit rays, {name}: n {n} p10/p25/p50/p75/p90 ' +
          '/'.join('%+.4f' % v[int(q * (n - 1))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)) +
          f'  frac < -0.05 {sum(1 for x in v if x < -0.05) / n:.3f}')
sgrep('ALL flight', flight)
sgrep('LOSS swaps', loss)
sgrep('loss lag -2/-1/+1/+2', [fl_m[idx[s] + g][1] for g in (-2, -1, 1, 2) for s in loss if s in idx and 0 <= idx[s] + g < len(fl_m)])
sgrep('loss +-3 s', [shifted(s, g) for g in (-3, 3) for s in loss if s in SWM])
def conrep(name, sws):
    sws = [x for x in sws if x in A]; n = len(sws)
    if not n: return
    c9 = sum(1 for x in sws if any(r is not None and r < 0.9 for r in A[x]['ray'][:3])) / n
    pc = [A[x]['pcd'] for x in sws if A[x]['pcd']]
    pcr = sum(1 for h, b in pc if b is not None and b < 0.9); pcc = sum(1 for h, b in pc if b is not None and b < 0.9 and not h)
    print(f'CONTRADICTION {name:22s} n {n:5d}: rendered wall < 0.9 f20 along a retail ray from the pushed eye {c9:.3f} | corner-3 '
          f're-test from the same pos: render crosses < 0.9 on {pcr}/{len(pc)}, of which the game calls clear {pcc}')
conrep('ALL flight', flight); conrep('LOSS', loss)
conrep('loss lag +-1,+-2', [fl_m[idx[x] + g][1] for g in (-2, -1, 1, 2) for x in loss if x in idx and 0 <= idx[x] + g < len(fl_m)])
conrep('loss +-3 s', [shifted(x, g) for g in (-3, 3) for x in loss if x in SWM])
def rxrep(name, sws):
    v = [A[x]['rxd'] for x in sws if x in A and A[x]['rxd']]
    if not v: print(f'HEIGHT {name}: n=0'); return
    d = sorted(a for a, o in v); n = len(d)
    print(f'HEIGHT render minus game height sample under the camera (rx), {name}: n {n} p10/p25/p50/p75/p90 ' +
          '/'.join('%+.4f' % d[int(q * (n - 1))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)) +
          f'  |d|<0.01 {sum(1 for a in d if abs(a) < 0.01) / n:.3f}  render above (>+0.05) {sum(1 for a in d if a > 0.05) / n:.3f}')
    return v
v = rxrep('ALL flight', flight); rxrep('LOSS', loss)
if v:
    g = defaultdict(list)
    for a, o in v: g[(int(((o[0] / 2.0) % 1.0) * 4), int(((o[2] / 2.0) % 1.0) * 4))].append(a)
    print('HEIGHT p50 by position in the 2-unit cell (rows z quarter 0..3, cols x quarter 0..3), (n):')
    for iz in range(4):
        print('   ' + ' '.join(('%+.3f(%4d)' % (sorted(g[(ix, iz)])[len(g[(ix, iz)]) // 2], len(g[(ix, iz)]))) if g[(ix, iz)] else '     -     ' for ix in range(4)))
    g2 = defaultdict(list)
    for a, o in v:
        fx = (o[0] / 0.5) % 1.0; fz = (o[2] / 0.5) % 1.0; g2[int(max(min(fx, 1 - fx), min(fz, 1 - fz)) * 10)].append(abs(a))
    print('HEIGHT |d| p50 by distance to the nearest 0.5-lattice line (x0.05 u): ' + ' '.join('%d:%.4f(%d)' % (k, sorted(g2[k])[len(g2[k]) // 2], len(g2[k])) for k in sorted(g2)))
def agree(name, sws, TH=0.95):
    sws = [x for x in sws if x in A and A[x]['rmask'] is not None]; M = Counter()
    for x in sws:
        for k in range(4):
            rc = A[x]['ray'][k] is not None and A[x]['ray'][k] < TH; gc = bool(A[x]['rmask'] >> k & 1); M[(rc, gc)] += 1
    n = sum(M.values()) or 1
    print(f'AGREE {name:22s} rays {n:6d} (render<{TH} f20 vs game exit re-test inside, same origin + offset): both {M[(True, True)]} '
          f'render-only {M[(True, False)]} game-only {M[(False, True)]} neither {M[(False, False)]}; '
          f'P(game inside | render inside) {M[(True, True)] / max(M[(True, True)] + M[(True, False)], 1):.3f}')
agree('ALL flight', flight); agree('LOSS', loss)
def agree_t(name, sws):
    sws = [x for x in sws if x in A and A[x]['rmask'] is not None]; M = Counter()
    for x in sws:
        for k in range(4):
            r = A[x]['ray'][k]
            if r is None or r >= 0.95: continue
            M[(min(int(r / 0.25), 3), bool(A[x]['rmask'] >> k & 1))] += 1
    print(f'AGREE-BY-DEPTH {name}: ' + '  '.join('t %.2f-%.2f game-inside %d/%d' % (b * 0.25, min(b * 0.25 + 0.25, 0.95), M[(b, True)], M[(b, True)] + M[(b, False)]) for b in range(4)))
agree_t('ALL flight', flight); agree_t('LOSS', loss)
agree('loss lag +-1,+-2', [fl_m[idx[x] + g][1] for g in (-2, -1, 1, 2) for x in loss if x in idx and 0 <= idx[x] + g < len(fl_m)])
agree('loss +-3 s', [shifted(x, g) for g in (-3, 3) for x in loss if x in SWM])
print('per loss swap: sw ntri near-frac (emitted part) ray-t[0..3] (x = no crossing) retail-hits mindist')
for s in loss:
    if s not in A: print(f'  sw {s} no record/tick'); continue
    a = A[s]
    print(f"  sw {s:5d} ntri {a['nt']:2d} near {a['nf']:.3f} ({a['nfe']:.3f}) rays " +
          ' '.join('x' if x is None else '%.2f' % x for x in a['ray']) + f" hits {a['hits']} exit-mask {a['rmask']} mind {a['mind']:.3f}")

# ---- s7114 LOD split (fps60-wall-lod): eye-cell LOD byte from the s7105 'ce' line (g= cell 24 = dz 0 dx 0, hex nibble 2 = lod)
# built just before the swap. Drawn TriGen modes: lod 0 = TriGen0000 (5x5 nodes, 32 tris), lod 1 = TriGen0001 (every other node,
# 3x3, 8 tris), lod 2 = TriGen02 (4 corners, 2 tris). The collision (0x80067D90 / sampleTerrainAtNpcPosition) always interpolates
# the full 5x5 tile heights, so H-coarse predicts |d| ~ 0 at lod 0 and the mismatch at lod 1/2.
CE = []
for line in open(pushf, errors='replace'):
    if not line.startswith('ce '): continue
    mm = re.search(r' m=(\d+) .* g=([0-9a-f]{196})', line)
    if mm: c = mm.group(2)[24 * 4:24 * 4 + 4]; CE.append((int(mm.group(1)), int(c[1], 16) if c[0] != '0' else -1))
CE.sort(); cem = [x[0] for x in CE]
def lod_of(sw):
    j = bisect.bisect_right(cem, SWM.get(sw, 0)) - 1
    return CE[j][1] if j >= 0 and SWM[sw] - CE[j][0] < 40 * 24000 else None
print(f'\nLOD SPLIT (s7114): ce lines {len(CE)}')
for lv in (0, 1, 2):
    S = [s for s in flight if lod_of(s) == lv]
    nt = sorted(A[s]['nt'] for s in S if s in A)
    print(f'  lod {lv}: flight swaps {len(S)}, loss swaps {sum(1 for s in loss if lod_of(s) == lv)}/{len(loss)}, '
          f'eye-cell tris p10/p50/p90 ' + ('/'.join(str(nt[int(q * (len(nt) - 1))]) for q in (0.1, 0.5, 0.9)) if nt else '-'))
    rxrep(f'lod {lv} flight', S); rxrep(f'lod {lv} loss', [s for s in loss if lod_of(s) == lv]); conrep(f'lod {lv} flight', S)
print('  loss swaps with no ce lod:', sum(1 for s in loss if lod_of(s) is None))
