#!/usr/bin/env python3
"""s6975 G1e: same-run before/after score for ROGUESQ_GFX_QOS_AT. Splits at the "[gfx-qos] t=<mach s>" stderr mark.
Per window: gfx send_dl wall - thread-CPU gap (R rows of ROGUESQ_G1E_GRING; s6975 showed late lock presents carry 4-12 ms of it vs
normal p99 1.7) as p50/p99 and rate of gaps > 3 ms per minute; send_dl wall p50/p99 and CPU p50; single-vsync-late presents
(P->P 30-40 ms, ring) and longer (>40) per minute. Positive control: the BEFORE window must show gaps > 3 ms (> 0) or a null after is
not a result.  usage: g1e_gfx_qos_ab.py gring.txt ring.txt log.txt [--from 95] [--guard 5] [--split-at S]"""
import sys, re
a = sys.argv[1:]; t_from = 95.0; guard = 5.0
if '--from' in a: i = a.index('--from'); t_from = float(a[i + 1]); del a[i:i + 2]
if '--guard' in a: i = a.index('--guard'); guard = float(a[i + 1]); del a[i:i + 2]
# s6981: a sham split has no real switch to settle, so its guard hole only hides events (s6980 Nr1 lost its one late at 180.1 s)
guard_set = '--guard' in sys.argv[1:]
# s6976: --split-at S = sham mark S s after the first row, for NO-QoS control runs (time-in-mission confound check)
sham = None
if '--split-at' in a: i = a.index('--split-at'); sham = float(a[i + 1]); del a[i:i + 2]
gf, rf, lf = a
if sham is None:
    mk = [float(m.group(1)) for m in re.finditer(r'\[gfx-qos\] t=([0-9.]+) mode=\d+ ok=1', open(lf, errors='replace').read())]
    if not mk: sys.exit('no ok=1 [gfx-qos] mark in log')
    tq = mk[0]
R = []
for l in open(gf, errors='replace'):
    if l.startswith('R ') and ' sdc=' in l and l.endswith('\n'):
        p = l.split(); R.append((float(p[1]), float(p[2][3:]), float(p[3][4:])))
P = []
for l in open(rf, errors='replace'):
    p = l.split()
    if len(p) > 2 and p[0] == 'P' and l.endswith('\n'):
        kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
        try:
            if float(kv.get('at', 0)) > 0: P.append(float(kv['at']))
        except ValueError: pass
P.sort(); t0 = min(R[0][0], P[0])
if sham is not None: tq = t0 + sham
if sham is not None and not guard_set: guard = 0.0
pc = lambda v, q: sorted(v)[int(q * (len(v) - 1))] if v else float('nan')
print(f'qos mark at {tq - t0:.1f} s since first row; windows [{t_from:.0f}, {tq - t0:.0f}) vs [{tq - t0 + guard:.0f}, end)')
print('window  |  dur s | n R  | gap p50  p99 | gap>3/min | sd p50  p99 | cpu p50 | late30-40/min | >40/min')
for nm, lo, hi in (('before', t0 + t_from, tq), ('after', tq + guard, 1e18)):
    r = [x for x in R if lo <= x[0] < hi]
    if not r: print(nm, 'empty'); continue
    dur = (r[-1][0] - r[0][0]) / 60.0
    g = [x[1] - x[2] for x in r]
    pp = [b for b in P if lo <= b < hi]
    d = [(pp[i] - pp[i - 1]) * 1e3 for i in range(1, len(pp))]
    print('%-7s | %6.1f | %4d | %5.2f %5.2f | %9.2f | %5.2f %5.2f | %7.2f | %13.2f | %7.2f' % (nm, dur * 60, len(r), pc(g, .5), pc(g, .99),
          sum(x > 3 for x in g) / dur, pc([x[1] for x in r], .5), pc([x[1] for x in r], .99), pc([x[2] for x in r], .5),
          sum(30 <= x < 40 for x in d) / dur, sum(x >= 40 for x in d) / dur))
