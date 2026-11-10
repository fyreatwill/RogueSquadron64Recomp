#!/usr/bin/env python3
"""s7104 fps60-wall-terrain-cull: near-eye terrain cell keep/cull verdicts (cc lines, tools/apply_s7104_cellcull.py) on
near-wall episode windows vs ordinary flight. Episode times/alignment exactly as tools/s7103_residual.py.
Verdicts: E empty footprint, S height-span reject, F s7030 cull, C pool cap, N no mesh, K kept, . not visited, V visited/undecided.
usage: s7104_cellcull.py push.txt drops.csv split.txt"""
import sys, re, ast
from collections import Counter
pf, dcsv, spl = sys.argv[1:4]
C = []
for l in open(pf, errors='replace'):
    if not l.startswith('cc '): continue
    d = dict(re.findall(r'(\w+)=(\S+)', l))
    try:
        C.append(dict(m=int(d['m']), g=d['g'], n=[int(x) for x in d['n'].split(',')], kept=int(d['kept']), cap=int(d['cap']),
                      win=[int(x) for x in d['win'].split(',')], ec=[int(x) for x in d['ec'].split(',')],
                      e=[float(x) for x in d['e'].split(',')], a=d['a'], b=d['b'], r3=d['r3'], r4=d['r4']))
    except (ValueError, KeyError):
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
hx = lambda s, i: None if s[2 * i:2 * i + 2] == '..' else (lambda v: v - 256 if v > 127 else v)(int(s[2 * i:2 * i + 2], 16))
print('cc calls %d episodes %d (t0=%.1f s)' % (len(C), len(ep), (C[0]['m'] - cap0) / 24e6 if C else 0))
# positive control: whole-window verdict counts
tot = [sum(c['n'][k] for c in C) for k in range(6)]
fire = [sum(1 for c in C if c['n'][k]) for k in range(6)]
print('control whole-window E,S,F,C,N,K totals', tot, ' calls with >0:', fire, ' cap hit calls', sum(1 for c in C if c['n'][3]))
for name, sel in (('episode', lambda c: inep(c['m'])), ('flight', lambda c: not inep(c['m']))):
    S = [c for c in C if sel(c)]
    if not S: continue
    print('%s calls %d' % (name, len(S)))
    for r in range(4):
        cnt = Counter(c['g'][i] for c in S for i in range(49) if ring[i] == r)
        n = sum(cnt.values())
        print('  ring %d: ' % r + ' '.join('%s %.2f%%' % (k, 100. * cnt[k] / n) for k in '.EVSFCNK' if cnt[k]))
    nk = Counter(sum(1 for i in range(49) if ring[i] <= 1 and c['g'][i] != 'K') for c in S)
    print('  calls by #non-K cells in ring<=1:', dict(sorted(nk.items())))
print('episodes: per call, ring<=1 3x3 verdicts (rows dz-1..1) | ring2-3 non-K count | kept cap | eye y | cell(ec) A,B r3,r4 for the eye cell')
for e in ep:
    S = [c for c in C if win(c['m'], e)]
    if not S: continue
    print('t=%.1f calls %d' % ((e - cap0) / 24e6, len(S)))
    for c in S:
        g = c['g']; c33 = '/'.join(g[(3 + dz) * 7 + 2:(3 + dz) * 7 + 5] for dz in (-1, 0, 1))
        far = sum(1 for i in range(49) if ring[i] >= 2 and g[i] != 'K')
        sp = ' '.join('%s:%s,%s/%s,%s' % (g[i], hx(c['a'], i), hx(c['b'], i), hx(c['r3'], i), hx(c['r4'], i)) for i in (23, 24, 25) if g[i] in 'SK')
        print('  %s%6.3f %s far%2d kept %4d/%d y %.2f ec %d,%d win %s  %s' % ('|' if c['m'] > e else ' ', (c['m'] - e) / 24e6, c33, far, c['kept'], c['cap'],
              c['e'][1], c['ec'][0], c['ec'][1], ','.join(map(str, c['win'])), sp))
