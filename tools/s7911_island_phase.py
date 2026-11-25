#!/usr/bin/env python3
"""s7911 G3 pre-flight island classifier: half-frame time phase vs state drift, at a FIXED content lag.

s7910 showed m11 island B is a load shift (content lag jumps by stall-delta/2). An island whose best content lag does NOT
move (tools/s7910_fork_lag.py) is either
  H-phase: the same time-keyed animation sampled at a sub-frame offset (s7870 island A: port tri YL lies between retail
           j and j+1, offset regresses ~0.5 x per-frame speed, b ~ 0; the differing-tri count stays flat), or
  H-drift: game state diverging (s7869/s7870 state class: offset not proportional to speed, the set of differing tris
           grows frame by frame, rank pairing fails on many frames).
Per frame j in [LO,HI): port multiset P[j] vs retail R[j-LAG]; port-only and retail-only tris rank-paired by YL, plus the
retail j-LAG+1 movers (tris of R[j-L+1] not in R[j-L]) and j-L-1 movers. Prints: frames with diffs, diff-count first/last
quarter means (growth), rank-pairable frames, between-ness fraction (fwd and bwd), regression offset = f*speed + b.
Classification rule: H-phase iff between >= 0.8, |f-0.5| <= 0.15 and growth ratio last/first <= 2; H-drift otherwise.
Control (iron rule 1, same invocation): --ctl LO:HI:LAG on a pair known to be H-phase (m6 island A, s7892 m6s3c) must
classify H-phase, rc 3 otherwise.
usage: s7911_island_phase.py RETAIL.bin[.zst] PORT.bin[.zst] LO:HI:LAG [--ctl-pair R P LO:HI:LAG]
"""
import sys, os, importlib.util, tempfile, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rs64_zopen

a = sys.argv[1:]
ctl = None
if '--ctl-pair' in a:
    i = a.index('--ctl-pair'); ctl = a[i + 1:i + 4]; del a[i:i + 4]
if len(a) != 3: print(__doc__); sys.exit(2)
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
tmp = tempfile.mkdtemp(prefix='s7911_')


def tris(c):
    return collections.Counter({k: v for k, v in c.items() if k[0] == 'tri'})


def classify(rp, pp, spec, name):
    lo, hi, L = map(int, spec.split(':'))
    R = [tris(c) for c, _ in m.frames(rs64_zopen.materialize(rp, tmp), True)]
    P = [tris(c) for c, _ in m.frames(rs64_zopen.materialize(pp, tmp), False)]
    ndiff = []; pair = btw = btwb = tot = 0; xs = []; ys = []
    for j in range(lo, min(hi, len(P))):
        r = j - L
        if r < 1 or r + 1 >= len(R): continue
        d = P[j] - R[r]; q = R[r] - P[j]
        ndiff.append(sum(d.values()) + sum(q.values()))
        py = sorted(k[-1] for k in d.elements()); ry = sorted(k[-1] for k in q.elements())
        ny = sorted(k[-1] for k in (R[r + 1] - R[r]).elements()); by = sorted(k[-1] for k in (R[r - 1] - R[r]).elements())
        if py and len(py) == len(ry):
            pair += 1
            if len(ny) == len(py):
                for x, y, z in zip(ry, py, ny):
                    tot += 1; btw += min(x, z) <= y <= max(x, z); xs.append(z - x); ys.append(y - x)
            if len(by) == len(py):
                btwb += sum(min(x, z) <= y <= max(x, z) for x, y, z in zip(ry, py, by))
    nz = sum(1 for v in ndiff if v); q4 = max(1, len(ndiff) // 4)
    g0 = sum(ndiff[:q4]) / q4; g1 = sum(ndiff[-q4:]) / q4; gr = g1 / g0 if g0 else float('inf') if g1 else 1.0
    f = b = float('nan')
    if len(xs) > 2:
        N = len(xs); mx = sum(xs) / N; my = sum(ys) / N; sxx = sum((x - mx) ** 2 for x in xs)
        if sxx: f = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx; b = my - f * mx
    bf = btw / tot if tot else 0.0
    cls = 'H-phase' if (bf >= 0.8 and abs(f - 0.5) <= 0.15 and gr <= 2) else 'H-drift'
    print(f'{name}: port[{lo}:{hi}) lag {L}: frames {len(ndiff)} with-diff {nz}; diff tris first-q {g0:.1f} last-q {g1:.1f} '
          f'(growth {gr:.2f}); rank-pairable {pair}; between fwd {btw}/{tot} ({bf:.2f}) bwd {btwb}; '
          f'offset = {f:.3f}*speed + {b:.3f} over {len(xs)} tris -> {cls}')
    return cls


ok = True
if ctl:
    c = classify(ctl[0], ctl[1], ctl[2], 'control')
    ok = c == 'H-phase'; print('control:', 'PASS' if ok else 'FAIL')
classify(a[0], a[1], a[2], 'subject')
sys.exit(0 if ok else 3)
