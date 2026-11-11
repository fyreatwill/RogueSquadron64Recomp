#!/usr/bin/env python3
"""s7106 fps60-wall-rsp-clip: RDP triangles per F5 TRI_GEN for the 9 terrain cells around the eye, near-wall episode windows vs
ordinary flight (rt lines from src/rsp/s7106_rsptri.cpp, ROGUESQ_S7106_RSPTRI=<file>; episode times/alignment as tools/s7105_emit.py).
Controls: tall (ucode DMEM parse) vs tbr (bridge count of forwarded tris) per swap; TRI_GEN class tri-count modes; near-key coverage.
usage: s7106_rsptri.py rt.txt drops.csv split.txt"""
import sys, re, ast
from collections import Counter
rf, dcsv, spl = sys.argv[1:4]
R = []
for l in open(rf, errors='replace'):
    if not l.startswith('rt '): continue
    d = dict(re.findall(r'(\w+)=(\S+)', l))
    try:
        near = []
        for s in d['n'].split(';'):
            f = s.split(',')
            if f[-1] == '-': near.append(dict(seen=int(f[0]), t=0, z=int(f[2]), dg=0, bb=None))
            else: near.append(dict(seen=int(f[0]), t=int(f[1]), z=int(f[2]), dg=int(f[3]), bb=tuple(int(x) for x in f[4:8])))
        cls = []
        for k in range(4):
            f = d['c%d' % k].split(','); mode = f[5].split(':')
            cls.append(dict(n=int(f[0]), t=int(f[1]), z=int(f[2]), mn=int(f[3]), mx=int(f[4]), mode=int(mode[0]), mc=int(mode[1])))
        R.append(dict(m=int(d['m']), sw=int(d['sw']), ntg=int(d['ntg']), ttg=int(d['ttg']), tall=int(d['tall']), tbr=int(d['tbr']),
                      mis=int(d['mis']), cls=cls, near=near, kp=int(d['kp']), k4=d['k4']))
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
print('rt swaps %d, episodes %d, t0=%.1f s' % (len(R), len(ep), (R[0]['m'] - cap0) / 24e6 if R else 0))
if not R: sys.exit(1)
F = [r for r in R if r['ntg'] > 0]
ta, tb = sum(r['tall'] for r in F), sum(r['tbr'] for r in F)
eq = sum(1 for r in F if r['tall'] == r['tbr'])
dif = sorted(abs(r['tall'] - r['tbr']) for r in F)
print('control tall vs tbr over %d TRI_GEN swaps: sum %d vs %d (ratio %.4f), equal swaps %d, |diff| median %d p90 %d; parse overruns %d'
      % (len(F), ta, tb, ta / max(tb, 1), eq, dif[len(dif) // 2], dif[int(len(dif) * .9)], sum(r['mis'] for r in R)))
print('control TRI_GEN share of tris: %.3f' % (sum(r['ttg'] for r in F) / max(ta, 1)))
for k, nm in enumerate(('mode0 sub0', 'mode0 sub1', 'mode2', 'other')):
    n = sum(r['cls'][k]['n'] for r in F); t = sum(r['cls'][k]['t'] for r in F); z = sum(r['cls'][k]['z'] for r in F)
    md = Counter(r['cls'][k]['mode'] for r in F if r['cls'][k]['n']).most_common(3)
    print('  class %-10s cmds %9d tris/cmd %.2f zero-tri %.4f  per-swap modal count %s  max %d' % (nm, n, t / max(n, 1), z / max(n, 1), md,
          max((r['cls'][k]['mx'] for r in F), default=0)))
print('control near keys published per swap', Counter(r['kp'] for r in F).most_common(4))
for name, sel in (('flight', lambda r: not inep(r['m'])), ('episode', lambda r: inep(r['m']))):
    S = [r for r in F if sel(r)]
    if not S: continue
    print('%s swaps %d' % (name, len(S)))
    for j in range(9):
        seen = sum(1 for r in S if r['near'][j]['seen']); cmds = sum(r['near'][j]['seen'] for r in S)
        t = sum(r['near'][j]['t'] for r in S); z = sum(r['near'][j]['z'] for r in S); dg = sum(r['near'][j]['dg'] for r in S)
        print('  slot %d (dz %+d dx %+d): swaps seen %5.1f%%  cmds %6d tris/cmd %6.2f zero-tri cmds %.4f degen/tri %.3f' % (j, j // 3 - 1, j % 3 - 1,
              100. * seen / len(S), cmds, t / max(cmds, 1), z / max(cmds, 1), dg / max(t, 1)))
print('episodes: per swap  dt  | slot tris (seen) for slots 0..8 | eye-cell bbox | tall tbr')
for e in ep:
    S = [r for r in F if win(r['m'], e)]
    if not S: continue
    print('t=%.1f swaps %d' % ((e - cap0) / 24e6, len(S)))
    for r in S:
        print('  %s%6.3f %s  bb4 %s  %d %d k4 %s' % ('|' if r['m'] > e else ' ', (r['m'] - e) / 24e6,
              ' '.join('%3d(%d)' % (n['t'], n['seen']) for n in r['near']), r['near'][4]['bb'], r['tall'], r['tbr'], r['k4']))
