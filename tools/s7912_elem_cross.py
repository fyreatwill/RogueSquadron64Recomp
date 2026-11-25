#!/usr/bin/env python3
"""s7912 G3: is a det-pair island element deterministic across runs? Extracts ONE draw-context element (texture image key +
combine, as printed by tools/s7912_island_ctx.py) from N RDP bins, aligns each on the element's first frame, and compares every
pair: element frames exact, symmetric-diff tris, plus the element's first/last frame and tri total per bin.
Reading: two same-config port runs exact + port vs retail not = the element is deterministic port state that differs from
retail (config/history dependent); same-config port runs differ = port nondeterminism (host timing reaches the element).
Control (iron rule 1, same run): each bin vs itself with one tri's YH planted +1 must give symdiff exactly 2, exact frames n-1.
usage: s7912_elem_cross.py TEX COMBINE NAME=PATH[:r] ...   (:r = retail 20-byte headers)
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]
if len(a) < 4: print(__doc__); sys.exit(2)
CT = (a[0], a[1])
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7912_island_ctx.py')).read().split('lag, j0, j1, cj')[0]
g = {'__name__': 's7912ctx', '__file__': __file__}; sv = sys.argv; sys.argv = ['x'] * 7; exec(src, g); sys.argv = sv
E = {}; ok = True
for spec in a[2:]:
    name, path = spec.split('=', 1); ret = path.endswith(':r'); path = path[:-2] if ret else path
    el = [collections.Counter(t[0] for t in f if t[1][1:3] == CT) for f in g['frames'](path, ret)]
    fs = [i for i, c in enumerate(el) if c]
    if not fs: print(f'{name}: element absent'); ok = False; continue
    E[name] = el[fs[0]:fs[-1] + 1]
    print(f'{name}: element frames {fs[0]}..{fs[-1]} ({fs[-1] - fs[0] + 1}), tris {sum(sum(c.values()) for c in E[name])}')
def cmp(A, B):
    n = min(len(A), len(B)); ex = sum(A[i] == B[i] for i in range(n))
    sd = sum(sum(((A[i] - B[i]) + (B[i] - A[i])).values()) for i in range(n)); return n, ex, sd
for k, A in E.items():
    B = [collections.Counter(c) for c in A]; m = len(B) // 2; e = next(iter(B[m])); B[m][e] -= 1
    B[m] = +B[m]; e2 = list(e); e2[1] = (e2[1] & ~0x3FFF) | ((e2[1] + 1) & 0x3FFF); B[m][tuple(e2)] += 1
    n, ex, sd = cmp(A, B); good = sd == 2 and ex == n - 1; ok &= good
    print(f'control {k} plant: exact {ex}/{n} symdiff {sd} -> {"PASS" if good else "FAIL"}')
ks = list(E)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        n, ex, sd = cmp(E[ks[i]], E[ks[j]]); print(f'{ks[i]} vs {ks[j]}: element frames exact {ex}/{n}, symdiff tris {sd}')
sys.exit(0 if ok else 3)
