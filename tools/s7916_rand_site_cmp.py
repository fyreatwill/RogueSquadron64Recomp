#!/usr/bin/env python3
"""s7916 G3 m6 island B: does the particle element follow the rand stream? Per arm (ROGUESQ_RAND_TRACE text, rows
'idx vi site value'; marker/probe rows dropped as in s7845_rng_tick_cmp.py) builds the per-caller-site value sequence.
For every pair: sites whose sequences are identical, and the first global divergence (index, VI, site).
Selector test: given the set of pairs known EXACT on the element (--exact A:B,...), report sites whose sequence
equality matches the element verdict on EVERY pair (equal on exact pairs, different on all others), and the same
for a VI window (--vi lo:hi). Control (iron rule 1, same run): a copy of the first arm with one value of its most
frequent site flipped must compare unequal on exactly that site vs the original.
usage: s7916_rand_site_cmp.py [--exact A:B,..] [--vi lo:hi] NAME=PATH ..."""
import sys, subprocess, collections, itertools
MARKS = {0x800027C0, 0x8006BEC8, 0x8006C018, 0x8006C010, 0x800AF374, 0x800C6674, 0x8008EE08, 0x8008EE84,
         0x800989D8, 0x80098DE0, 0x80099720, 0x800998E8, 0x800FA730}
a = sys.argv[1:]; exact = set(); vi = None; arms = {}
while a:
    x = a.pop(0)
    if x == '--exact': exact = {frozenset(p.split(':')) for p in a.pop(0).split(',')}
    elif x == '--vi': vi = tuple(map(int, a.pop(0).split(':')))
    else: n, p = x.split('=', 1); arms[n] = p
if len(arms) < 2: print(__doc__); sys.exit(2)
def load(p):
    txt = subprocess.run(['zstd', '-dc', p], capture_output=True, text=True).stdout if p.endswith('.zst') else open(p).read()
    rows = []
    for l in txt.splitlines():
        f = l.split()
        if len(f) != 4: continue
        s = int(f[2], 16)
        if s in MARKS or s >> 24 != 0x80: continue
        rows.append((int(f[1]), s, int(f[3], 16)))
    return rows
def persite(rows, w=None):
    d = collections.defaultdict(list)
    for v, s, x in rows:
        if w is None or w[0] <= v <= w[1]: d[s].append(x)
    return d
R = {n: load(p) for n, p in arms.items()}
for n, r in R.items(): print(f'{n}: rand rows {len(r)}, VI {r[0][0]}..{r[-1][0]}, sites {len(set(s for _, s, _ in r))}')
ok = True
# control
n0 = next(iter(R)); base = persite(R[n0]); top = max(base, key=lambda s: len(base[s]))
pl = {s: list(v) for s, v in base.items()}; pl[top][len(pl[top]) // 2] ^= 1
diff = [s for s in base if base[s] != pl[s]]; good = diff == [top]; ok &= good
print(f'control plant {n0} site {top:08x}: unequal sites {[hex(s) for s in diff]} -> {"PASS" if good else "FAIL"}')
pairs = list(itertools.combinations(R, 2))
for w, tag in ((None, 'whole run'), (vi, f'VI {vi}') if vi else (None, None)):
    if tag is None: continue
    P = {n: persite(r, w) for n, r in R.items()}
    sites = sorted(set().union(*P.values()))
    print(f'--- {tag}: {len(sites)} sites')
    for A, B in pairs:
        eq = sum(P[A].get(s) == P[B].get(s) for s in sites)
        ra = [x for x in R[A] if w is None or w[0] <= x[0] <= w[1]]; rb = [x for x in R[B] if w is None or w[0] <= x[0] <= w[1]]
        fd = next((i for i in range(min(len(ra), len(rb))) if ra[i][1:] != rb[i][1:]), None)
        fds = f'idx {fd} VI {ra[fd][0]}/{rb[fd][0]} site {ra[fd][1]:08x}/{rb[fd][1]:08x}' if fd is not None else 'none'
        tagx = 'EXACT' if frozenset((A, B)) in exact else ''
        print(f'{A} vs {B} {tagx}: equal sites {eq}/{len(sites)}, seq first diff {fds}')
    if exact:
        sel = [s for s in sites if all((P[A].get(s) == P[B].get(s)) == (frozenset((A, B)) in exact) for A, B in pairs)]
        print('selector sites (equal on exact pairs, unequal on all others):',
              [(hex(s), {n: len(P[n].get(s, [])) for n in P}) for s in sel][:20])
        eqx = [s for s in sites if all(P[A].get(s) == P[B].get(s) for A, B in pairs if frozenset((A, B)) in exact)]
        print(f'sites equal on every exact pair: {len(eqx)}/{len(sites)}')
sys.exit(0 if ok else 3)
