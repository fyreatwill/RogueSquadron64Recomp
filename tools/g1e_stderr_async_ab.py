#!/usr/bin/env python3
"""s6979 same-run A/B for ROGUESQ_STDERR_ASYNC_AT: per send_dl window (g1e_late_leg.py --windows), Gfx-thread samples in
UNINTERRUPTIBLE (state 4, ROGUESQ_G1E_THREADS census) and those whose stack is in write(); wall-cpu (sd-sdc) tail, before vs after
the "[stderr-async] on t=" marker (or --split-at <mach s>). Positive control: the before half must show write() U samples.
usage: g1e_stderr_async_ab.py thr.bin windows.txt log.txt [--split-at T] [--from-start S]"""
import sys, runpy, io, contextlib, bisect, re
a = sys.argv[1:]; split = None; fs = 95.0
if '--split-at' in a: i = a.index('--split-at'); split = float(a[i + 1]); del a[i:i + 2]
if '--from-start' in a: i = a.index('--from-start'); fs = float(a[i + 1]); del a[i:i + 2]
thr, winf, logf = a
if split is None:
    for l in open(logf, errors='replace'):
        m = re.search(r'\[stderr-async\] on t=([0-9.]+)', l)
        if m: split = float(m.group(1)); break
sys.argv = ['x', thr, winf]  # census exits early without a windows file
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(__file__.replace('g1e_stderr_async_ab.py', 'g1e_thread_census.py'))
S, St, G, K, E, sym = g['S'], g['St'], g['G'], g['K'], g['E'], g['sym']
t_first = St[0]
Kd = {k[0]: k[1] for k in K}
def is_write(st): return any(sym.get(x, ('',))[0] in ('__write_nocancel', 'write') for x in st[:2])
Ut = [(e[0], is_write(Kd.get(e[0], ()))) for e in E if e[1] == 4]; Uts = [u[0] for u in Ut]
W = [tuple(map(float, l.split()[1:4])) for l in open(winf)]
pc = lambda v, q: sorted(v)[int(q * (len(v) - 1))] if v else float('nan')
print(f'split at mach {split} (= {split - t_first:.1f} s into the census); windows from {fs:.0f} s')
for lab, cond in (('before (direct stderr)', lambda t: t < split), ('after (async stderr)', lambda t: t >= split)):
    ws = [w for w in W if cond(w[0]) and w[0] - t_first >= fs]
    u = uw = 0; hit = 0
    for te, sd, sdc in ws:
        i0 = bisect.bisect_left(Uts, te - sd / 1e3); i1 = bisect.bisect_right(Uts, te); n = i1 - i0; u += n; uw += sum(Ut[i][1] for i in range(i0, i1)); hit += n > 0
    gap = [sd - sdc for te, sd, sdc in ws]; mins = max(1e-9, (ws[-1][0] - ws[0][0]) / 60) if ws else 1
    print(f'  {lab}: windows {len(ws)} over {mins:.2f} min; U samples {u} ({u / mins:.1f}/min), of them write() {uw}; windows with U {hit}; '
          f'wall-cpu p50 {pc(gap, .5):.2f} p99 {pc(gap, .99):.2f} p999 {pc(gap, .999):.2f} max {max(gap) if gap else float("nan"):.2f} ms; >3 ms {sum(x > 3 for x in gap)} ({sum(x > 3 for x in gap) / mins:.1f}/min)')
