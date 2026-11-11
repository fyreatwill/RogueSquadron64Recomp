#!/usr/bin/env python3
"""s7115 fps60-wall-gap: exact eye-cell surface vs the render near pyramid and the push-out probe rays (offline, no rebuild).

usage: s7115_neargap.py push.txt tris.bin losscan.txt   (an s7114 capture: CHASE + ROGUESQ_S7114_HSRC hx lines + G5B_TRIS clock)

Surface: the 25 bytes of the y-clamp tile under the camera (hx), node (i, j) at x0 + 0.5 i, z0 + 0.5 j with x0 = o.x - (qx + fx) 0.5,
  z0 = o.z - (qz + fz) 0.5 (o from the same tick's rx), y = s8 * sc / 256 + y0, 00-11 diagonal (s7114_hsrc coll()). Under
  NEARLOD=16 on-seconds this is the drawn eye-cell mesh exactly (s7114).
Camera: eye = bv rd of the tick, r/u/f basis from the pu corner frame (s7113 basis()), near n = 30/256 = 0.1172, half-tans from
  s7108 ([s7108] lines, constant): horizontal 1.368, vertical 0.637. Probe rays = the 4 corner offsets (c - p0) from the eye.
Per tick:
  under  : eye below the surface at its own xz (inside the terrain)
  pierce : some screen ray (33 x 17 grid over the near rectangle) meets the surface at depth < n (that part of the wall is cut)
  frac   : fraction of the screen grid cut that way (on in-tile samples)
  ray    : any of the 4 corner probe segments (eye -> eye + corner) crosses the surface; game: any pu hit flag of the tick
  out    : fraction of near-pyramid sample points outside the tile (H-tile: the crossing lies on a neighbour's bytes)
Controls: (1) surface at o == hx h; (2) surface at the game's own pu hit points (hit=1, inside the tile) == hp.y;
  (3) positive: the surface moved 1 u toward the eye (dy -1, y is down) must make pierce/under ~1 on all ticks (instrument can say yes).
Groups: eye-cell near-z loss swaps (s7108 rule), all flight swaps, losses shifted +-3 s; each split by NEARLOD on/off seconds."""
import sys, re, mmap, struct, bisect, math, collections
pushf, trisb, lsc = sys.argv[1:4]
FC = '80138458'; NEAR = 30 / 256.0; TX, TY = 1.368, 0.637
kv = re.compile(r'(\w+)=(\S+)'); V = lambda s: [float(x) for x in s.split(',')]
sub = lambda a, b: [x - y for x, y in zip(a, b)]
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def nrm(a):
    l = math.sqrt(dot(a, a)); return [x / l for x in a]

T = []; cur = None; lasthx = None
for line in open(pushf, errors='replace'):
    k = line[:3]
    if k == 'hx ':
        d = dict(kv.findall(line))
        if d['tl'] == '00000000': lasthx = None; continue
        q = [int(x) for x in d['q'].split(',')]; fr = V(d['fr'])
        b = [x - 256 if x > 127 else x for x in bytes.fromhex(d['b'])]
        lasthx = dict(qx=q[0], qz=q[1], fx=fr[0], fz=fr[1], h=float(d['h']), sc=float(d['sc']), y0=float(d['y0']), b=b); continue
    if k not in ('ch ', 'pu ', 'bv ', 'rx ', 'pc '): continue
    d = dict(kv.findall(line))
    if d.get('cam') != FC: continue
    if k == 'ch ': cur = {'m': int(d['m']), 'pu': [], 'bv': None, 'rx': None, 'hx': None}; T.append(cur); lasthx = None
    elif cur is None: continue
    elif k == 'pu ': cur['pu'].append((int(d['i']), int(d['hit']), V(d['c']), V(d['pre']), V(d['hp'])))
    elif k == 'rx ':
        if 'p0' not in d or 'o' not in d: continue  # s7118: line torn by an interleaved/killed write
        cur['rx'] = V(d['o']); cur['p0'] = V(d['p0']); cur['hx'] = lasthx
    elif k == 'bv ' and cur['bv'] is None: cur['bv'] = (int(d['m']), V(d['rd']))

def basis(t):
    pu = [x for x in t['pu'] if x[0] in (0, 1, 2)][:3]
    if len(pu) < 3 or [x[0] for x in pu] != [0, 1, 2]: return None
    o = [sub(x[2], pu[0][3]) for x in pu]
    r = nrm(sub(o[1], o[0])); u = nrm(sub(o[2], o[1])); f = nrm(cross(r, u))
    if dot(o[0], f) < 0: f = [-x for x in f]
    o.append([o[0][k] + o[2][k] - o[1][k] for k in range(3)])  # corner 3 = 0 + 2 - 1
    return r, u, f, o

def surf(t, dy=0.0):
    hx = t['hx']; o = t['rx']; b = hx['b']; sc, y0 = hx['sc'], hx['y0']
    x0 = o[0] - (hx['qx'] + hx['fx']) * 0.5; z0 = o[2] - (hx['qz'] + hx['fz']) * 0.5
    def H(x, z):
        X = (x - x0) / 0.5; Z = (z - z0) / 0.5
        if X < 0 or Z < 0 or X > 4 or Z > 4: return None
        qx, qz = min(int(X), 3), min(int(Z), 3); fx, fz = X - qx, Z - qz
        v = qz * 5 + qx; h00, h01, h10, h11 = b[v], b[v + 1], b[v + 5], b[v + 6]
        if fx - fz >= 0: c = h01 + (1 - fx) * (h00 - h01) + fz * (h11 - h01)
        else: c = h10 + fx * (h11 - h10) + (1 - fz) * (h00 - h10)
        return c * sc / 256.0 + y0 + dy
    return H

GX = [(-1 + 2 * i / 32) for i in range(33)]; GY = [(-1 + 2 * j / 16) for j in range(17)]
TS = [k / 12 for k in range(1, 13)]
def geo(e, bs, H, smax=1.0):
    """near-pyramid cut (screen rays meeting the surface at depth < smax * near) and corner-ray crossings from eye e"""
    r, u, f, co = bs
    cut = 0; tot = 0; out = 0; npts = 0; dmin = None
    for gx in GX:
        for gy in GY:
            dvec = [f[k] + gx * TX * r[k] + gy * TY * u[k] for k in range(3)]  # depth 1 along f
            hit = False; seen = False
            for s in TS:
                s *= smax
                p = [e[k] + s * NEAR * dvec[k] for k in range(3)]
                h = H(p[0], p[2]); npts += 1
                if h is None: out += 1; continue
                seen = True
                if p[1] > h:
                    hit = True; dmin = s if dmin is None else min(dmin, s); break
            if seen: tot += 1; cut += hit and (dmin is not None)
    ray = False
    for c in co:
        for s in [k / 16 for k in range(1, 17)]:
            p = [e[k] + s * c[k] for k in range(3)]; h = H(p[0], p[2])
            if h is not None and p[1] > h: ray = True; break
        if ray: break
    return cut, tot, out, npts, dmin, ray
def analyse(t, dy=0.0):
    bs = basis(t); H = surf(t, dy); e = t['bv'][1]
    he = H(e[0], e[2])
    under = he is not None and e[1] > he  # y points DOWN: the y clamp keeps pos.y <= h - mg (eye-surf == -mg on clamped ticks)
    cut, tot, out, npts, _, ray = geo(e, bs, H)
    *_, dmin, _ = geo(e, bs, H, 3.0)  # nearest surface depth along screen rays (near units), up to 3 near
    p0 = t['p0']; pc, ptot, _, _, _, rayp = geo(p0, bs, H)
    game = any(x[1] for x in t['pu'] if x[0] in (0, 1, 2))
    mv = [e[k] - p0[k] for k in range(3)]
    h0 = H(p0[0], p0[2]); under0 = h0 is not None and p0[1] > h0  # loop-start pos already inside the terrain
    return dict(under=under, pierce=cut > 0, frac=cut / max(tot, 1), ray=ray, game=game, out=out / max(npts, 1),
                dmin=dmin, under0=under0, cls=('U' if under0 else ('P' if game else 'N')), pierce0=pc > 0, ray0=rayp, mvy=mv[1], mvh=math.hypot(mv[0], mv[2]),
                ey=(e[1] - he) if he is not None else None)

TU = [t for t in T if t['bv'] and t['rx'] and t['hx'] and basis(t)]
print(f'flight ticks {len(T)}, usable (bv+rx+hx+basis) {len(TU)}')
# control 1
c1 = sorted(abs(surf(t)(t['rx'][0], t['rx'][2]) - t['hx']['h']) for t in TU)
print(f'CONTROL 1 surface at o vs hx h: n {len(c1)} p50 {c1[len(c1) // 2]:.2e} max {c1[-1]:.2e}')
c2 = []
for t in TU:
    H = surf(t)
    for i, hit, c, pre, hp in t['pu']:
        if hit and i in (0, 1, 2):
            h = H(hp[0], hp[2])
            if h is not None: c2.append(abs(h - hp[1]))
c2.sort()
print(f'CONTROL 2 surface at game pu hit points (in tile) vs hp.y: n {len(c2)} p50 {c2[len(c2) // 2]:.2e} p90 {c2[int(0.9 * len(c2))]:.2e} '
      f'<1e-3 {sum(1 for x in c2 if x < 1e-3) / max(len(c2), 1):.3f}' if c2 else 'CONTROL 2 n 0')

F = open(trisb, 'rb'); dm = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ)
M = b'\xf5\xf5\xf5\xf5'; SWM = {}; p = dm.find(M)
while p >= 0:
    n = dm.find(M, p + 16)
    while n > 0 and (n - p - 16) % 32: n = dm.find(M, n + 1)
    tt, q = struct.unpack_from('<QI', dm, p + 4); SWM[q] = tt; p = n
bm = [t['bv'][0] for t in TU]
def tick_m(m):
    j = bisect.bisect_left(bm, m) - 1
    if j < 0 or m - bm[j] > 40 * 24e3: return None
    return TU[j]
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
loss = []
for line in open(lsc):
    g = rl.search(line)
    if not g or float(g.group(2)) < 0: continue
    if "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100 and int(g.group(1)) in SWM: loss.append(int(g.group(1)))
par = lambda m: int(m / 24e6) & 1
fl = sorted(SWM[s] for s in SWM if tick_m(SWM[s]))
print(f'swaps {len(SWM)}, with a usable tick {len(fl)}; eye-cell near-z losses {len(loss)}, with a tick {sum(1 for s in loss if tick_m(SWM[s]))}')

cache = {}
def A(t, dy=0.0):
    key = (id(t), dy)
    if key not in cache: cache[key] = analyse(t, dy)
    return cache[key]
def rep(name, ms, dy=0.0):
    ts = [tick_m(m) for m in ms]; ts = [t for t in ts if t]
    n = len(ts)
    if not n: print(f'  {name:30s} n 0'); return
    a = [A(t, dy) for t in ts]
    fr = sorted(x['frac'] for x in a); pi = [x for x in a if x['pierce']]
    ey = sorted(x['ey'] for x in a if x['ey'] is not None)
    g = lambda k: sum(1 for x in a if x[k]) / n
    gap = sum(1 for x in pi if not x['ray']) / max(len(pi), 1); gapg = sum(1 for x in pi if not x['game']) / max(len(pi), 1)
    print(f'  {name:30s} n {n:5d} under {g("under"):.3f} pierce {g("pierce"):.3f} frac p50/p90 {fr[n // 2]:.3f}/{fr[(9 * n) // 10]:.3f} '
          f'ray {g("ray"):.3f} game-hit {g("game"):.3f} | pierce&no-ray {gap:.3f} pierce&no-game-hit {gapg:.3f} | out p50 '
          f'{sorted(x["out"] for x in a)[n // 2]:.3f} | eye-surf p10/p50 {ey[len(ey) // 10]:+.3f}/{ey[len(ey) // 2]:+.3f}')
    dm = sorted(x['dmin'] if x['dmin'] is not None else 9 for x in a)
    pn = [x for x in a if x['pierce']]
    print(f'  {"":30s} depth-to-surface (near units, 9 = > 3) p10/p50/p90 {dm[n // 10]:.2f}/{dm[n // 2]:.2f}/{dm[(9 * n) // 10]:.2f} '
          f'<1.5 {sum(1 for x in dm if x < 1.5) / n:.3f} | from p0 (pre-move): pierce {g("pierce0"):.3f} ray {g("ray0"):.3f} | '
          f'pierce now but not from p0 {sum(1 for x in pn if not x["pierce0"]) / max(len(pn), 1):.3f} | move y p50 '
          f'{sorted(x["mvy"] for x in a)[n // 2]:+.3f} horiz p50 {sorted(x["mvh"] for x in a)[n // 2]:.3f}')
    for c in 'UPN':
        cs = [x for x in a if x['cls'] == c]
        print(f'  {"":30s} class {c} ({ {"U": "p0 inside terrain", "P": "pushed (game hit)", "N": "no hit, p0 outside"}[c]:20s}) '
              f'{len(cs) / n:.3f} (n {len(cs)}): pierce {sum(1 for x in cs if x["pierce"]) / max(len(cs), 1):.3f}'
              f' depth<1.5 {sum(1 for x in cs if x["dmin"] is not None and x["dmin"] < 1.5) / max(len(cs), 1):.3f}')
lm = [SWM[s] for s in loss]
sh = lambda ms, d: [m + d * 24e6 for m in ms]
import random; random.seed(7115)
fs = random.sample(fl, min(3000, len(fl)))
print('CONTROL 3 (surface moved 1 u toward the eye, must read ~1):'); rep('flight sample -1u', fs[:500], -1.0)
for lab, sel in (('all', lambda m: True), ('on (NEARLOD lod0 exact)', lambda m: par(m) == 1), ('off', lambda m: par(m) == 0)):
    print(f'== {lab}')
    rep('eye-cell near-z LOSS', [m for m in lm if sel(m)])
    rep('loss -3 s', [m for m in sh(lm, -3) if sel(m)]); rep('loss +3 s', [m for m in sh(lm, 3) if sel(m)])
    rep('flight sample', [m for m in fs if sel(m)])
print('per loss: t(s) on under pierce frac ray game out eye-surf | dmin pierce0 ray0 move-y move-h')
for m in lm:
    t = tick_m(m)
    if not t: print(f'  {m / 24e6:9.2f} no tick'); continue
    a = A(t)
    print(f'  {m / 24e6:9.2f} {par(m)} {int(a["under"])} {int(a["pierce"])} {a["frac"]:.3f} {int(a["ray"])} {int(a["game"])} {a["out"]:.2f} '
          + (f'{a["ey"]:+.3f}' if a['ey'] is not None else '-')
          + f' | {a["dmin"] if a["dmin"] is not None else 9:.2f} {int(a["pierce0"])} {int(a["ray0"])} {a["mvy"]:+.3f} {a["mvh"]:.3f} {a["cls"]}')

# ---- per-ray agreement: game pu hit flag vs exact geometry of the same segment pre -> c (all usable ticks, rays fully in tile)
#   seg : the segment pre -> c crosses the surface anywhere;  end : the endpoint c alone is inside the terrain;
#   pre : the start point pre is already inside (a downward-crossing test from inside sees nothing)
lossT = set(id(tick_m(m)) for m in lm if tick_m(m))
AG = {False: collections.Counter(), True: collections.Counter()}
for t in TU:
    H = surf(t)
    for i, hit, c, pre, hp in t['pu']:
        if i not in (0, 1, 2): continue
        pts = [[pre[k] + s / 32 * (c[k] - pre[k]) for k in range(3)] for s in range(33)]
        hs = [H(p[0], p[2]) for p in pts]
        if any(h is None for h in hs): AG[id(t) in lossT]['outoftile'] += 1; continue
        ins = [p[1] > h for p, h in zip(pts, hs)]
        AG[id(t) in lossT][(hit, any(ins), ins[-1], ins[0])] += 1
for k in (False, True):
    print(f'RAY AGREEMENT ({"loss ticks" if k else "all other ticks"}): (game hit, seg crosses, end inside, pre inside) -> rays')
    for key, v in sorted(AG[k].items(), key=lambda x: -x[1]): print(f'   {key}: {v}')

# ---- what test does the game run? hit rate binned by the exact minimum clearance along the segment (h - y, y down: > 0 above)
#   and, on hits, where the game's hit point sits (fraction of pre -> c) vs the exact first crossing
BIN = collections.defaultdict(lambda: [0, 0]); HF = []
for t in TU:
    H = surf(t)
    for i, hit, c, pre, hp in t['pu']:
        if i not in (0, 1, 2): continue
        pts = [[pre[k] + s / 64 * (c[k] - pre[k]) for k in range(3)] for s in range(65)]
        hs = [H(p[0], p[2]) for p in pts]
        if any(h is None for h in hs): continue
        cl = [h - p[1] for p, h in zip(pts, hs)]
        if cl[0] < 0: continue  # start inside: reported above
        mc = min(cl); b = round(max(-0.5, min(0.5, mc)) * 20) / 20
        BIN[b][0] += 1; BIN[b][1] += hit
        if hit:
            L = math.dist(pre, c); fh = math.dist(pre, hp) / L if L else 0
            fx = next((s / 64 for s, x in enumerate(cl) if x < 0), None)
            HF.append((fh, fx, mc))
print('GAME HIT RATE vs exact min clearance along pre->c (start outside; <0 = segment enters the terrain):')
print('   ' + ' '.join(f'{b:+.2f}:{v[1]}/{v[0]}' for b, v in sorted(BIN.items())))
hf = [x for x in HF if x[1] is not None]
d = sorted(abs(a - b) for a, b, _ in hf)
print(f'hits with an exact crossing {len(hf)}/{len(HF)}: |game hit frac - exact crossing frac| p50 {d[len(d) // 2]:.3f} p90 {d[int(0.9 * len(d))]:.3f}' if d else '')
nh = sorted(x[2] for x in HF if x[1] is None)
if nh: print(f'hits with no exact crossing: min clearance p10/p50/p90 {nh[len(nh) // 10]:.3f}/{nh[len(nh) // 2]:.3f}/{nh[(9 * len(nh)) // 10]:.3f}; '
              f'game hit frac p50 {sorted(x[0] for x in HF if x[1] is None)[len(nh) // 2]:.3f}')
