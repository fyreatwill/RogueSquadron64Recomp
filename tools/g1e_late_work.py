#!/usr/bin/env python3
"""s6982 G1e: split the residual late-present send_dl CPU inflation into H-ucode-work / H-slowcore / H-cache.
usage: g1e_late_work.py win.txt gring.txt [--pcpus 5-9] [--from S]
win.txt  = g1e_late_leg.py --windows output ('late|norm <send_dl end mach s> <sd ms> <sdc ms>')
gring.txt = ROGUESQ_G1E_GRING with s6982 R fields: it= (ucode L_1090 passes), rb= (RDP bytes), c0/c1 (CPU at send_dl start/end),
            cs= (CPU histogram of every 256th ucode pass).
--pcpus: perflevel0 CPU ids. Default 5-9 = this M5 Pro, from the s6982 QoS control (scratch/s6982/cpunum.c: BACKGROUND QoS threads
never ran on 5-9; hw.perflevel0.logicalcpu=5).
Work model: least squares on normal presents, sdc ~ a*it + b*rb + c. Per late: work (it, rb) vs normal p99, residual cpu vs normal
residual p99, P fraction of the cs samples. Positive control: normal tasks run wholly on E must show a higher ms/kiter than wholly
on P (the instrument can see core speed), and the fit must explain the normal sdc spread (R^2 reported)."""
import sys, bisect
args = sys.argv[1:]; P = set(range(5, 10)); t_from = 0.0
if '--pcpus' in args:
    i = args.index('--pcpus'); a, b = args[i + 1].split('-'); P = set(range(int(a), int(b) + 1)); del args[i:i + 2]
if '--from' in args:
    i = args.index('--from'); t_from = float(args[i + 1]); del args[i:i + 2]
winf, gf = args
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
R = []
for l in open(gf, errors='replace'):
    if not (l.startswith('R ') and ' it=' in l and l.endswith('\n')): continue
    p = l.split(); kv = dict(x.split('=', 1) for x in p[2:])
    cs = {}
    for x in kv.get('cs', '').split(','):
        if ':' in x: c, n = x.split(':'); cs[int(c)] = int(n)
    R.append((float(p[1]), float(kv['sd']), float(kv['sdc']), int(kv['it']), int(kv['rb']), int(kv['c0']), int(kv['c1']), cs))
if not R: sys.exit('no s6982 R rows (it=) in gring')
Rt = [r[0] for r in R]
rows = {'late': [], 'norm': []}; miss = 0
for l in open(winf):
    p = l.split()
    if len(p) < 4: continue
    t = float(p[1]); j = bisect.bisect_left(Rt, t - 1e-5)
    if j < len(R) and abs(R[j][0] - t) < 1e-4: rows[p[0]].append(R[j])
    else: miss += 1
t0 = R[0][0]
for k in rows: rows[k] = [r for r in rows[k] if r[0] - t0 >= t_from]
N, L = rows['norm'], rows['late']
print(f'R rows {len(R)}, joined norm {len(N)} late {len(L)}, unjoined windows {miss}')
if len(N) < 20: sys.exit('too few normal rows')
def pfrac(r):
    tot = sum(r[7].values()); return sum(n for c, n in r[7].items() if c in P) / tot if tot else float('nan')
# fit sdc ~ a*it + b*rb + c (3x3 normal equations)
X = [(r[3] / 1e3, r[4] / 1e5, 1.0) for r in N]; y = [r[2] for r in N]
A = [[sum(x[i] * x[j] for x in X) for j in range(3)] for i in range(3)]; B = [sum(x[i] * v for x, v in zip(X, y)) for i in range(3)]
def solve(A, B):
    M = [row[:] + [b] for row, b in zip(A, B)]
    for c in range(3):
        piv = max(range(c, 3), key=lambda r: abs(M[r][c])); M[c], M[piv] = M[piv], M[c]
        for r in range(3):
            if r != c:
                f = M[r][c] / M[c][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [M[i][3] / M[i][i] for i in range(3)]
co = solve(A, B)
pred = lambda r: co[0] * r[3] / 1e3 + co[1] * r[4] / 1e5 + co[2]
res = [r[2] - pred(r) for r in N]; my = sum(y) / len(y)
r2 = 1 - sum(e * e for e in res) / sum((v - my) ** 2 for v in y)
print(f'fit sdc = {co[0]:.3f}*kiter + {co[1]:.3f}*(100kB RDP) + {co[2]:.3f} ms, R^2 {r2:.3f} on normals')
mk = lambda r: r[2] / (r[3] / 1e3) if r[3] else float('nan')
allP = [mk(r) for r in N if pfrac(r) == 1.0]; allE = [mk(r) for r in N if pfrac(r) == 0.0]
print(f'control ms/kiter normal: wholly-P n={len(allP)} p50 {pc(allP,.5):.3f}  wholly-E n={len(allE)} p50 {pc(allE,.5):.3f}'
      f'  (pass if E > P)  normal Pfrac p50 {pc([pfrac(r) for r in N],.5):.2f}')
for nm, f in (('sdc', lambda r: r[2]), ('kiter', lambda r: r[3] / 1e3), ('RDPkB', lambda r: r[4] / 1e3), ('ms/kiter', mk), ('resid', lambda r: r[2] - pred(r))):
    v = [f(r) for r in N]; print(f'  normal {nm:8s} p50 {pc(v,.5):8.3f} p99 {pc(v,.99):8.3f}')
CL = {'E0-4': set(range(0, 5)), 'P5-9': set(range(5, 10)), 'E10-14': set(range(10, 15))}
def dom(r):
    tot = sum(r[7].values())
    for k, s in CL.items():
        if tot and sum(n for c, n in r[7].items() if c in s) >= 0.9 * tot: return k
    return 'mixed' if tot else 'nosample'
print('per dominant cluster (>=90% of cs samples), normal tasks: n, ms/kiter p50, fit residual p50/p99 ms')
for k in list(CL) + ['mixed', 'nosample']:
    g = [r for r in N if dom(r) == k]
    if g: print(f'  {k:8s} n={len(g):6d} ms/kiter {pc([mk(r) for r in g],.5):.3f}  resid {pc([r[2]-pred(r) for r in g],.5):+.3f} / {pc([r[2]-pred(r) for r in g],.99):+.3f}')
p99 = {'it': pc([r[3] for r in N], .99), 'rb': pc([r[4] for r in N], .99), 'res': pc(res, .99), 'mk': pc([mk(r) for r in N], .99)}
print('per late: t  sdc  kiter  RDPkB  ms/kiter  resid  Pfrac  c0>c1  cluster  verdict')
tally = {}
for r in L:
    work = r[3] > p99['it'] or r[4] > p99['rb']; slow = (r[2] - pred(r)) > p99['res']; pf = pfrac(r)
    v = ('H-ucode-work' if work and not slow else 'H-slowcore' if slow and pf < 0.5 else 'H-cache' if slow else
         'both(work+slow)' if work else 'none>p99')
    if work and slow: v = 'both(work+slow,%s)' % ('E' if pf < 0.5 else 'P')
    tally[v] = tally.get(v, 0) + 1
    print(f'  {r[0]-t0:8.1f} {r[2]:6.2f} {r[3]/1e3:6.1f} {r[4]/1e3:7.1f} {mk(r):7.3f} {r[2]-pred(r):+6.2f} {pf:5.2f}  {r[5]:>2}>{r[6]:<2} {dom(r):8s} {v}')
print('tally', tally)
# s6982 summary: H-migrate (cold cache after leaving the home cluster) vs work. home = commonest dominant cluster of normal tasks.
import collections
home = collections.Counter(dom(r) for r in N).most_common(1)[0][0]
off = lambda g: sum(1 for r in g if dom(r) != home) / len(g) if g else float('nan')
on_res = [r[2] - pred(r) for r in N if dom(r) == home]; off_res = [r[2] - pred(r) for r in N if dom(r) != home]
print(f'SUMMARY home={home} normal off-home {off(N):.3f} late off-home {off(L):.3f} | resid p50 home {pc(on_res,.5):+.2f} off {pc(off_res,.5):+.2f} ms'
      f' | kiter p50 normal {pc([r[3] for r in N],.5)/1e3:.1f} late {pc([r[3] for r in L],.5)/1e3:.1f} | lates {len(L)}')
