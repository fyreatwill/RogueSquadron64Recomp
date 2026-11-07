#!/usr/bin/env python3
"""s6944 G1e: split the slow seconds of a [g1b]+[g1e-split]+[g1b-gt] log (ROGUESQ_G1B=1 ROGUESQ_G1E_AQ=2) against the full-rate ones.
usage: g1e_tail_split.py LOG [--t0 100] [--slow 57] [--gthr 8]
Per wall second: tasks (send_dl count), sd_wall/sd_cpu (send_dl ms, mean), ucode (factor5 ucode wall incl. in-ucode submits),
calls (rsp_dpc_submit per task), game thread cpu/blocked ms. Prints group means (tasks<=slow vs tasks==60), the
deltas, Pearson r of each term with tasks, and the wall-cpu gap distribution (the host-stall term; its max shows it is live).
Reading: CPU (sd_cpu) growth = H-scene/H-range; gap growth = H-stall; sd_wall-sd_cpu not growing also rules out a wait (H-fence)."""
import re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('--t0', type=int, default=100)
ap.add_argument('--slow', type=int, default=57); ap.add_argument('--gthr', default='8'); a = ap.parse_args()
rows, sp, gt = [], None, {}
for l in open(a.log, errors='replace'):
    if l.startswith('[g1e-split]'): sp = dict(re.findall(r'(\w+)=([\d.]+)', l))
    elif l.startswith('[g1b-gt]'):
        t = int(re.search(r't=(\d+)', l).group(1))
        for s, o, c, b in re.findall(r' (\d+)\.(\d+):(\d+)/(\d+)', l): gt.setdefault(t, {})[s] = (int(c), int(b))
    elif l.startswith('[g1b]'):
        d = dict(re.findall(r'(\w+)=([\d./]+)', l)); sw, swm = d['sd_wall'].split('/'); sc, scm = d['sd_cpu'].split('/')
        r = dict(t=int(d['t']), tasks=int(d['tasks']), sw=float(sw), swm=float(swm), sc=float(sc), scm=float(scm))
        if sp: r.update(uc=float(sp['ucode_ms']), calls=float(sp['calls']))
        rows.append(r)
rows = [r for r in rows if r['t'] >= a.t0 and 'uc' in r]
for r in rows:
    c, b = gt.get(r['t'], {}).get(a.gthr, (0, 0)); r['gcpu'] = c; r['gblk'] = b; r['gap'] = r['sw'] - r['sc']; r['nonuc'] = r['sc'] - r['uc']
def corr(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    c = sum((p - mx) * (q - my) for p, q in zip(x, y)); vx = sum((p - mx) ** 2 for p in x); vy = sum((q - my) ** 2 for q in y)
    return c / (vx * vy) ** .5 if vx and vy else 0.0
K = ['sw', 'sc', 'gap', 'uc', 'nonuc', 'calls', 'swm', 'gcpu', 'gblk']
lo = [r for r in rows if r['tasks'] <= a.slow]; hi = [r for r in rows if r['tasks'] >= 60]
m = lambda g, k: sum(r[k] for r in g) / len(g) if g else float('nan')
print(f"seconds={len(rows)} slow(<= {a.slow})={len(lo)} full(60)={len(hi)}")
print('term     ' + ' '.join(f'{k:>8}' for k in K))
print('slow     ' + ' '.join(f'{m(lo,k):8.2f}' for k in K))
print('full     ' + ' '.join(f'{m(hi,k):8.2f}' for k in K))
print('delta    ' + ' '.join(f'{m(lo,k)-m(hi,k):8.2f}' for k in K))
T = [r['tasks'] for r in rows]
print('r(tasks) ' + ' '.join(f'{corr(T,[r[k] for r in rows]):8.3f}' for k in K))
g = sorted(r['gap'] for r in rows); gm = max(rows, key=lambda r: r['swm'] - r['scm'])
print(f"gap p50={g[len(g)//2]:.2f} p95={g[int(len(g)*.95)]:.2f} max={g[-1]:.2f}; worst per-task gap {gm['swm']-gm['scm']:.0f} ms at t={gm['t']} tasks={gm['tasks']}")
