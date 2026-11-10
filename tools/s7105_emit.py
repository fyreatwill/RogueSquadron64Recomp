#!/usr/bin/env python3
"""s7105 fps60-wall-mesh-emit: near-eye terrain cells, list -> render chain -> CPU TRI_GEN emit, on near-wall episode windows vs
ordinary flight (ce lines from tools/apply_s7105_emit.py; episode times/alignment exactly as tools/s7104_cellcull.py).
Per cell (4 hex): dup count in the list, lod byte, on the chain walked from the chain start, CPU emit visits.
States: '-' not in list, 'X' in list but never emitted, 'E' emitted once, 'M' emitted >1. (The chain bit = reachable from the far-cutoff
chain start s5; the renderer walks the whole list, rv == nl, so the bit is reported only as a side count.)
usage: s7105_emit.py push.txt drops.csv split.txt"""
import sys, re, ast
from collections import Counter
pf, dcsv, spl = sys.argv[1:4]
C = []
for l in open(pf, errors='replace'):
    if not l.startswith('ce '): continue
    d = dict(re.findall(r'(\w+)=(\S+)', l))
    try:
        g = d['g']; cells = [(int(g[4*i], 16), int(g[4*i+1], 16), int(g[4*i+2], 16), int(g[4*i+3], 16)) for i in range(49)]
        C.append(dict(m=int(d['m']), fc=int(d['fc']), nl=int(d['nl']), ch=int(d['ch']), rc=int(d['rc']), rs=int(d['rs']), rv=int(d['rv']),
                      uv=int(d['uv']), lod=[int(x) for x in d['lod'].split(',')], cells=cells, w=d['w'].split(','), ec=d['ec']))
    except (ValueError, KeyError, IndexError):
        pass
rows = [l.split(',') for l in open(dcsv)][1:]
cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6
ep = []
for l in open(spl, errors='replace'):
    g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
    if g:
        ts = ast.literal_eval(g.group(2)); ep += [cap0 + x * 24e6 for i, x in enumerate(ts) if i == 0 or x - ts[i - 1] > 1.0]
win = lambda m, e: e - 0.3 * 24e6 <= m <= e + 0.1 * 24e6
inep = lambda m: any(win(m, e) for e in ep)
ring = [max(abs(i % 7 - 3), abs(i // 7 - 3)) for i in range(49)]
st = lambda c: '-' if c[0] == 0 else ('X' if c[3] == 0 else ('E' if c[3] == 1 else 'M'))
print('ce gens %d episodes %d (t0=%.1f s)' % (len(C), len(ep), (C[0]['m'] - cap0) / 24e6 if C else 0))
if not C: sys.exit(1)
# positive controls
lh = [sum(c['lod'][k] for c in C) for k in range(4)]
print('control lod hist whole list (0,1,2,other):', lh, ' gens with >1 tier:', sum(1 for c in C if sum(1 for x in c['lod'][:3] if x) > 1))
print('control rfm calls/gen', Counter(c['rc'] for c in C).most_common(4), ' gens with rs>0', sum(1 for c in C if c['rs']),
      ' rv median', sorted(c['rv'] for c in C)[len(C)//2], ' chain median', sorted(c['ch'] for c in C)[len(C)//2],
      ' list median', sorted(c['nl'] for c in C)[len(C)//2], ' uv>0 gens', sum(1 for c in C if c['uv']))
print('control list == emitted count gens:', sum(1 for c in C if c['nl'] == c['rv']), 'of', len(C), ' rv<nl:', sum(1 for c in C if c['rv'] < c['nl']), ' rv>nl:', sum(1 for c in C if c['rv'] > c['nl']))
for r in range(4):
    lc = Counter(c['cells'][i][1] for c in C for i in range(49) if ring[i] == r and c['cells'][i][0])
    print('  lod by ring %d:' % r, dict(sorted(lc.items())))
for name, sel in (('episode', lambda c: inep(c['m'])), ('flight', lambda c: not inep(c['m']))):
    S = [c for c in C if sel(c)]
    if not S: continue
    print('%s gens %d' % (name, len(S)))
    for r in range(4):
        cnt = Counter(st(c['cells'][i]) for c in S for i in range(49) if ring[i] == r)
        n = sum(cnt.values())
        print('  ring %d: ' % r + ' '.join('%s %.2f%%' % (k, 100. * cnt[k] / n) for k in '-XEM' if cnt[k]))
    bad = Counter(sum(1 for i in range(49) if ring[i] <= 1 and st(c['cells'][i]) == 'X') for c in S)
    print('  gens by #ring<=1 cells in list but not emitted:', dict(sorted(bad.items())))
    dup = sum(1 for c in S for i in range(49) if c['cells'][i][0] > 1)
    print('  cells listed twice:', dup, ' X cells on the s5 chain:', sum(1 for c in S for i in range(49) if st(c['cells'][i]) == 'X' and c['cells'][i][2]))
print('episodes: per gen, ring<=1 3x3 states (rows dz-1..1) | lods | ring2-3 X count | chain/emitted | eye-cell w0')
for e in ep:
    S = [c for c in C if win(c['m'], e)]
    if not S: continue
    print('t=%.1f gens %d' % ((e - cap0) / 24e6, len(S)))
    for c in S:
        cs = c['cells']; idx = [(3 + dz) * 7 + 3 + dx for dz in (-1, 0, 1) for dx in (-1, 0, 1)]
        s33 = '/'.join(''.join(st(cs[i]) for i in idx[k:k+3]) for k in (0, 3, 6))
        l33 = '/'.join(''.join('%x' % cs[i][1] if cs[i][0] else '.' for i in idx[k:k+3]) for k in (0, 3, 6))
        far = sum(1 for i in range(49) if ring[i] >= 2 and st(cs[i]) == 'X')
        print('  %s%6.3f %s lod %s far %2d ch %4d rv %4d ec %s w0 %s' % ('|' if c['m'] > e else ' ', (c['m'] - e) / 24e6, s33, l33, far,
              c['ch'], c['rv'], c['ec'], c['w'][4]))
