#!/usr/bin/env python3
"""s7896 G3: classify island B (the tail of the 640 pre-flight scene, s7895) frame by frame on a det-pinned pair.

For every port frame j in [J0, J1) (absolute port indices) paired with retail j+OFF (OFF = the s7868 alignment offset,
recomputed here with the same unique-signature vote), report:
  R/P tri counts, port-only / retail-only tri counts (multiset), PRIM colours of the differing tris, texrect diffs,
  subset class (P<R: port lacks tris retail has = object absent; P>R: extra object; both: changed geometry),
  shift k: the k in [-K..K] for which P[j] == R[j+OFF+k] exactly (timing class: port shows retail's frame k later/earlier),
  and kbest: the k minimising the symmetric tri diff, with its size, plus 'geo-only' (same tri count and same PRIM multiset,
  edge coefficients differ = positions moved).
Hypotheses (NEXT s7896): H-object (whole PRIM groups present/absent), H-dt (frames match retail shifted by k / positions
only), H-rng (random-placed object only). Summary line tallies classes across the window.
Controls (iron rule 1, same run): (1) a frame of the longest exact run must classify as exact k=0; (2) a planted YH+1 on
one tri of that frame must classify as geo-only with diff 1/1; (3) a planted one-frame shift (port frame replaced by its
retail neighbour j+OFF+1) must report k=+1. rc 3 if any control fails.
usage: s7896_island_b_probe.py RETAIL.bin PORT.bin J0 J1 [--k 4] [--rows 40]
"""
import sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
a = sys.argv[1:]
if len(a) < 4: print(__doc__); sys.exit(2)
K = int(a[a.index('--k') + 1]) if '--k' in a else 4
ROWS = int(a[a.index('--rows') + 1]) if '--rows' in a else 40
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
R = [c for c, _ in m.frames(a[0], True)]; P = [c for c, _ in m.frames(a[1], False)]
j0, j1 = int(a[2]), int(a[3])
sig = lambda c: hash(frozenset(c.items()))
tri = lambda c: sum(v for k, v in c.items() if k[0] == 'tri')
rs = [sig(c) for c in R]; ps = [sig(c) for c in P]
rc = collections.Counter(rs); pc = collections.Counter(ps); rpos = {h: i for i, h in enumerate(rs)}
votes = collections.Counter(rpos[h] - j for j, h in enumerate(ps) if rc[h] == 1 and pc[h] == 1 and tri(P[j]) >= 1)
OFF = votes.most_common(1)[0][0]
print(f'frames retail {len(R)} port {len(P)}; offset {OFF} votes {votes.most_common(3)}')
# longest exact run (control frame source)
best = (0, 0); s = None
for j in range(len(P)):
    e = 0 <= j + OFF < len(R) and rs[j + OFF] == ps[j]
    if e and s is None: s = j
    if (not e or j == len(P) - 1) and s is not None:
        if j - s > best[0]: best = (j - s, s)
        s = None
print(f'longest exact run: port {best[1]}..{best[1] + best[0]} ({best[0]} frames)')

def classify(p, jr):
    r = R[jr] if 0 <= jr < len(R) else collections.Counter()
    po = p - r; ro = r - p
    pt = collections.Counter({k: v for k, v in po.items() if k[0] == 'tri'}); rt = collections.Counter({k: v for k, v in ro.items() if k[0] == 'tri'})
    ptx = sum(v for k, v in po.items() if k[0] != 'tri'); rtx = sum(v for k, v in ro.items() if k[0] != 'tri')
    ks = [k for k in range(-K, K + 1) if 0 <= jr + k < len(R) and R[jr + k] == p]
    kb = min(range(-K, K + 1), key=lambda k: (tri((p - R[jr + k]) + (R[jr + k] - p)) if 0 <= jr + k < len(R) else 1 << 30, abs(k)))
    kbd = tri((p - R[jr + kb]) + (R[jr + kb] - p)) if 0 <= jr + kb < len(R) else -1
    primp = collections.Counter(k[1] for k in pt.elements()); primr = collections.Counter(k[1] for k in rt.elements())
    np_, nr = sum(pt.values()), sum(rt.values())
    if np_ == 0 and nr == 0 and ptx == 0 and rtx == 0: cls = 'exact'
    elif np_ == 0 and nr == 0: cls = 'texrect'
    elif np_ == 0: cls = 'P<R'
    elif nr == 0: cls = 'P>R'
    elif np_ == nr and primp == primr: cls = 'geo-only'
    else: cls = 'mixed'
    return dict(rt=tri(r), pt=tri(p), np=np_, nr=nr, ptx=ptx, rtx=rtx, ks=ks, kb=kb, kbd=kbd, cls=cls,
                primp=primp.most_common(3), primr=primr.most_common(3))

# controls
cj = best[1] + best[0] // 2; ok = True
c0 = classify(P[cj], cj + OFF); ok &= c0['cls'] == 'exact' and 0 in c0['ks']
pp = P[cj].copy(); kk = next(k for k in pp if k[0] == 'tri'); g = list(kk); g[-1] = (g[-1] & ~0x3FFF) | ((g[-1] + 1) & 0x3FFF)
pp[kk] -= 1; pp[tuple(g)] += 1; pp += collections.Counter()
c1 = classify(pp, cj + OFF); ok &= c1['cls'] == 'geo-only' and c1['np'] == 1 and c1['nr'] == 1
c2 = classify(R[cj + OFF + 1], cj + OFF); shift_ok = 1 in c2['ks'] or R[cj + OFF + 1] == R[cj + OFF]
ok &= shift_ok
print(f'controls: exact={c0["cls"]} ks={c0["ks"]}; plant={c1["cls"]} {c1["np"]}/{c1["nr"]}; shift ks={c2["ks"]} -> {"PASS" if ok else "FAIL"}')

tally = collections.Counter(); kt = collections.Counter(); prim_all_p = collections.Counter(); prim_all_r = collections.Counter(); n = 0
for j in range(j0, j1):
    c = classify(P[j], j + OFF); tally[c['cls']] += 1; kt[tuple(c['ks']) if c['ks'] else ('kb%+d/%d' % (c['kb'], c['kbd']) if c['kbd'] == 0 else 'none')] += 1
    for pr, v in c['primp']: prim_all_p[pr] += v
    for pr, v in c['primr']: prim_all_r[pr] += v
    if n < ROWS:
        print(f'  p{j} r{j + OFF} tris R{c["rt"]} P{c["pt"]} port-only {c["np"]} retail-only {c["nr"]} tx+{c["ptx"]}/-{c["rtx"]} '
              f'{c["cls"]:8s} k={c["ks"]} kbest={c["kb"]:+d}/{c["kbd"]} primP {c["primp"]} primR {c["primr"]}')
        n += 1
print('class tally:', dict(tally)); print('shift tally:', kt.most_common(8))
print('top port-only PRIM:', prim_all_p.most_common(5)); print('top retail-only PRIM:', prim_all_r.most_common(5))
sys.exit(0 if ok else 3)
