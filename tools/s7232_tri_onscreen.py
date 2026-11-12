#!/usr/bin/env python3
"""s7232 G1c: are the extra triangles on screen? Scores the s7232 [g1cf] fields (ROGUESQ_G1CF=1 build >= s7232).

Per VI the RDP stream walk classifies every triangle against the current RDP scissor: tin (bbox meets it), tout (fully outside),
tzero (y span < 1 scanline, draws nothing), kpx (sum of scissor-clipped bboxes, kilo-px), bin0..7 (tin by bbox-centre x across the
scissor width), vout (classifier control: same tris vs a virtual scissor one full width to the right; must be ~ all tris that do not
reach past the right scissor edge).
[g1cf] lines are binned to the second closed by the next [g1b] t=N line, as in s7231_cost_decomp.py.
Prints per log, window (--t0..--t1) and flight: per-task tin/tout/tzero/kpx, the 8 x-bins as per-task counts, sd_wall, and the control
ratio vout/(tri) . Then, for every pair (A,B) given as --pair A=B (labels = log basenames), the per-task deltas A-B split into
tin/tout/tzero and outer (bins 0,7) vs inner bins: the outcome table for H-offscreen / H-onscreen / H-zero.
Usage: s7232_tri_onscreen.py log_a4.txt log_n4.txt ... [--t0 77 --t1 97] [--pair log_a4=log_n4]
"""
import re, sys, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument('logs', nargs='+')
ap.add_argument('--t0', type=int, default=77); ap.add_argument('--t1', type=int, default=97)
ap.add_argument('--flight0', type=int, default=60); ap.add_argument('--flight1', type=int, default=230)
ap.add_argument('--pair', action='append', default=[])
a = ap.parse_args()
G1B = re.compile(r'\[g1b\] t=(\d+) vi=\d+ tasks=(\d+) sd_wall=([\d.]+)/')
G1CF = re.compile(r'\[g1cf\] vi=\d+ dd=\d+ tasks=(\d+) .*? tri=(\d+) .*? tin=(\d+) tout=(\d+) tzero=(\d+) vout=(\d+) kpx=([\d.]+) '
                  r'sc=([\d,.-]+) bin=([\d,]+)')
KEYS = ['tasks', 'tri', 'tin', 'tout', 'tzero', 'vout', 'kpx'] + [f'b{i}' for i in range(8)]

def load(path):
    rows, acc, sc = [], dict.fromkeys(KEYS, 0.0), None
    with open(path, errors='ignore') as f:
        for ln in f:
            m = G1CF.match(ln)
            if m:
                v = [int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]), float(m[7])] + [int(x) for x in m[9].split(',')]
                for k, x in zip(KEYS, v): acc[k] += x
                sc = m[8]; continue
            m = G1B.match(ln)
            if m:
                rows.append(dict(acc, t=int(m[1]), sd=float(m[3]), sc=sc)); acc = dict.fromkeys(KEYS, 0.0)
    return rows

def summ(L):
    T = sum(r['tasks'] for r in L) or 1
    d = {k: sum(r[k] for r in L) / T for k in KEYS if k != 'tasks'}
    d['sd'] = sum(r['sd'] for r in L) / max(len(L), 1); d['n'] = len(L)
    d['ctl'] = d['vout'] / max(d['tri'], 1e-9)
    return d

res = {}
for p in a.logs:
    rows = [r for r in load(p) if a.flight0 <= r['t'] <= a.flight1 and r['tasks'] > 0]
    lab = os.path.basename(p).split('.')[0]
    if not rows: print(lab, 'no flight rows with s7232 [g1cf] fields'); continue
    w = [r for r in rows if a.t0 <= r['t'] < a.t1]
    res[lab] = (summ(w), summ(rows))
    scs = sorted({r['sc'] for r in rows if r['sc']})
    print(f'== {lab}: flight s={len(rows)} window s={len(w)} scissors={scs[:4]}')
    for name, d in (('window', res[lab][0]), ('flight', res[lab][1])):
        print(f'  {name:6s} sd={d["sd"]:.2f}ms  per task: tri={d["tri"]:.0f} tin={d["tin"]:.0f} tout={d["tout"]:.0f} tzero={d["tzero"]:.0f} '
              f'kpx={d["kpx"]:.0f}  ctl vout/tri={d["ctl"]:.3f}  bins=' + ' '.join(f'{d[f"b{i}"]:.0f}' for i in range(8)))
for pr in a.pair:
    A, B = pr.split('=')
    if A not in res or B not in res: print('pair missing', pr); continue
    for i, name in ((0, 'window'), (1, 'flight')):
        x, y = res[A][i], res[B][i]; D = {k: x[k] - y[k] for k in x if isinstance(x[k], float)}
        outer = D['b0'] + D['b7']; inner = sum(D[f'b{j}'] for j in range(1, 7)); tot = D['tri'] or 1e-9
        print(f'== {A} - {B} {name}: dsd={D["sd"]:+.2f}ms dtri={D["tri"]:+.0f} = tin {D["tin"]:+.0f} ({D["tin"]/tot:.0%}) + tout {D["tout"]:+.0f} '
              f'({D["tout"]/tot:.0%}) + tzero {D["tzero"]:+.0f} ({D["tzero"]/tot:.0%}); dtin outer bins {outer:+.0f} inner {inner:+.0f}; dkpx {D["kpx"]:+.0f}')
