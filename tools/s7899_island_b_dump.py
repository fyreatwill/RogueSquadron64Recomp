#!/usr/bin/env python3
"""s7899 G3 island B: name the drifting object. Dump the differing triangles (port-only vs retail-only, multiset) of a
det-pinned frame window with screen bbox/centroid/size, then split three hypotheses by the dx/dy of each port-only tri to its
nearest same-PRIM retail-only tri:
  H-cam        all pairs in a frame share one common delta (spread small vs |delta|)
  H-anim       per-frame median |delta| grows ~linearly with frame index
  H-object-rng pairs are random (no common delta, no trend); also tests 'permutation': port-only tri found verbatim in a
               retail frame within +-K (same set, other order / other frame) vs never seen in retail.
Control (iron rule 1, same run): a planted copy of one exact frame with one tri moved by (+8 px x, +4 px y) must (a) appear in
the dump as exactly 1 port-only + 1 retail-only tri at the planted bbox and (b) pair with delta (8, 4). rc 3 if it fails.
usage: s7899_island_b_dump.py RETAIL.bin PORT.bin J0 J1 [--off N] [--k 4] [--rows 12]
"""
import sys, os, collections, importlib.util, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
a = sys.argv[1:]
if len(a) < 4: print(__doc__); sys.exit(2)
opt = lambda n, d: int(a[a.index(n) + 1]) if n in a else d
K = opt('--k', 4); ROWS = opt('--rows', 12)
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
R = [c for c, _ in m.frames(a[0], True)]; P = [c for c, _ in m.frames(a[1], False)]
j0, j1 = int(a[2]), int(a[3])
sig = lambda c: hash(frozenset(c.items()))
if '--off' in a: OFF = opt('--off', 0)
else:
    rs = [sig(c) for c in R]; ps = [sig(c) for c in P]; rc = collections.Counter(rs); pc = collections.Counter(ps)
    rpos = {h: i for i, h in enumerate(rs)}
    OFF = collections.Counter(rpos[h] - j for j, h in enumerate(ps) if rc[h] == 1 and pc[h] == 1).most_common(1)[0][0]
print(f'frames retail {len(R)} port {len(P)} offset {OFF}')

def s14(v): v &= 0x3FFF; return (v - 0x4000 if v & 0x2000 else v) / 4.0
def s32(v): return (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
def bbox(k):
    w0, w1, XL, DL, XH, DH, XM, DM = k[2:10]
    yl, ym, yh = s14(w0), s14(w1 >> 16), s14(w1)
    xl, xh, xm, dh = s32(XL), s32(XH), s32(XM), s32(DH)
    xs = [xh, xm, xl, xh + dh * (yl - yh)]; ys = [yh, ym, yl]
    return (min(xs), min(ys), max(xs), max(ys))
def cen(b): return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
def tris(c): return collections.Counter({k: v for k, v in c.items() if k[0] == 'tri'})

def pairs(po, ro):
    """greedy nearest-centroid pairing within PRIM; returns [(port_k, retail_k, dx, dy)], unpaired counts"""
    out = []; rl = list(ro.elements()); used = [False] * len(rl)
    for pk in sorted(po.elements(), key=lambda k: cen(bbox(k))):
        pc_ = cen(bbox(pk)); best = None
        for i, rk in enumerate(rl):
            if used[i] or rk[1] != pk[1]: continue
            rc_ = cen(bbox(rk)); d = (pc_[0] - rc_[0]) ** 2 + (pc_[1] - rc_[1]) ** 2
            if best is None or d < best[0]: best = (d, i)
        if best: used[best[1]] = True; rk = rl[best[1]]; rc_ = cen(bbox(rk)); out.append((pk, rk, pc_[0] - rc_[0], pc_[1] - rc_[1]))
    return out, len(list(po.elements())) - len(out), used.count(False)

# control: plant on a far-earlier exact frame
cj = next(j for j in range(max(0, j0 - 400), j0) if 0 <= j + OFF < len(R) and P[j] == R[j + OFF] and len(tris(P[j])) > 3)
pp = P[cj].copy(); kk = sorted(tris(pp))[0]; g = list(kk)
g[4] = (g[4] + 8 * 65536) & 0xFFFFFFFF; g[6] = (g[6] + 8 * 65536) & 0xFFFFFFFF; g[8] = (g[8] + 8 * 65536) & 0xFFFFFFFF  # XL,XH,XM +8px
w0, w1 = g[2], g[3]; g[2] = (w0 & ~0x3FFF) | ((w0 + 16) & 0x3FFF)
g[3] = (w1 & 0xC000C000) | ((((w1 >> 16) + 16) & 0x3FFF) << 16) | ((w1 + 16) & 0x3FFF)  # y +4px
pp[kk] -= 1; pp[tuple(g)] += 1; pp += collections.Counter()
r = tris(R[cj + OFF]); p = tris(pp); po, ro = p - r, r - p; pr, up, ur = pairs(po, ro)
ok = len(list(po.elements())) == 1 and len(list(ro.elements())) == 1 and len(pr) == 1 and abs(pr[0][2] - 8) < .01 and abs(pr[0][3] - 4) < .01
print(f'control: plant frame p{cj} port-only {sum(po.values())} retail-only {sum(ro.values())} '
      f'bbox {tuple(round(x,1) for x in bbox(list(po)[0])) if po else None} delta {[(round(x[2],2), round(x[3],2)) for x in pr]} -> {"PASS" if ok else "FAIL"}')

allp = collections.defaultdict(set)   # retail tri keys per retail frame window for permutation test
SW, SH = [int(x) for x in (a[a.index('--screen') + 1] if '--screen' in a else '640,240').split(',')]
edge = lambda b: b[0] < 0 or b[1] < 0 or b[2] > SW or b[3] > SH
est = collections.Counter(); szb = collections.Counter()
sizeb = lambda b: 'big' if max(b[2] - b[0], b[3] - b[1]) >= 16 else 'small'
rows = 0; per = []; perm_hit = perm_tot = 0; boxes_p = []; boxes_r = []
for j in range(j0, j1):
    jr = j + OFF
    if not 0 <= jr < len(R): continue
    r = tris(R[jr]); p = tris(P[j]); po, ro = p - r, r - p
    if not po and not ro: continue
    pr, up, ur = pairs(po, ro)
    for k, v in (p & r).items(): b = bbox(k); est['common', edge(b)] += v; szb['common', sizeb(b)] += v
    for k, v in po.items(): b = bbox(k); est['diff', edge(b)] += v; szb['diff', sizeb(b)] += v
    near = set(k for kk_ in range(-K, K + 1) if 0 <= jr + kk_ < len(R) and kk_ != 0 for k in tris(R[jr + kk_]))
    farset = None
    for k in po.elements():
        perm_tot += 1; perm_hit += k in near
        boxes_p.append(bbox(k))
    for k in ro.elements(): boxes_r.append(bbox(k))
    dxs = [x[2] for x in pr]; dys = [x[3] for x in pr]
    if pr:
        md = (st.median(dxs), st.median(dys)); spread = st.median([abs(x - md[0]) + abs(y - md[1]) for x, y in zip(dxs, dys)])
        per.append((j, md, spread, st.median([abs(x) + abs(y) for x, y in zip(dxs, dys)]), len(pr)))
    if rows < ROWS:
        rows += 1
        print(f' p{j} r{jr} tris R{sum(r.values())} P{sum(p.values())} port-only {sum(po.values())} retail-only {sum(ro.values())} unpaired {up}/{ur}')
        for pk, rk, dx, dy in pr[:10]:
            b = bbox(pk); rb = bbox(rk)
            print(f'    {pk[1]} P bbox ({b[0]:.1f},{b[1]:.1f})-({b[2]:.1f},{b[3]:.1f}) size {b[2]-b[0]:.1f}x{b[3]-b[1]:.1f} | '
                  f'R ({rb[0]:.1f},{rb[1]:.1f}) size {rb[2]-rb[0]:.1f}x{rb[3]-rb[1]:.1f} | d ({dx:+.2f},{dy:+.2f}) inR+-{K} {pk in near}')
print(f'frames with diffs {len(per)}; permutation: port-only tris found verbatim in retail +-{K} frames {perm_hit}/{perm_tot}')
if per:
    import math
    mags = [x[3] for x in per]; sprs = [x[2] for x in per]
    n = len(per); xs = [x[0] for x in per]; mx = sum(xs) / n; my = sum(mags) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, mags)); sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in mags)
    corr = sxy / math.sqrt(sxx * syy) if sxx and syy else 0
    print(f'per-frame median |d| median {st.median(mags):.2f} (min {min(mags):.2f} max {max(mags):.2f}); within-frame spread median {st.median(sprs):.2f}; '
          f'corr(frame, |d|) {corr:+.2f} slope {sxy / sxx if sxx else 0:+.4f} px/frame')
    print('  first/last 5 frames (j, median d, spread, |d|, pairs):', [(x[0], tuple(round(v, 2) for v in x[1]), round(x[2], 2), round(x[3], 2), x[4]) for x in per[:5] + per[-5:]])
    for nm, B in (('port-only', boxes_p), ('retail-only', boxes_r)):
        if B:
            sz = [max(b[2] - b[0], b[3] - b[1]) for b in B]; cy = [(b[1] + b[3]) / 2 for b in B]; cx = [(b[0] + b[2]) / 2 for b in B]
            print(f'  {nm}: n {len(B)} size median {st.median(sz):.1f} max {max(sz):.1f}; x {min(cx):.0f}..{max(cx):.0f} y {min(cy):.0f}..{max(cy):.0f}')
fr = lambda c, t: f"{c[t, True]}/{c[t, True] + c[t, False]} = {c[t, True] / max(1, c[t, True] + c[t, False]):.3f}"
print(f'screen-edge-crossing tris ({SW}x{SH}): diff {fr(est, "diff")}; common (same frames) {fr(est, "common")}')
print(f'size: diff big {szb["diff", "big"]} small {szb["diff", "small"]}; common big {szb["common", "big"]} small {szb["common", "small"]}')
sys.exit(0 if ok else 3)
