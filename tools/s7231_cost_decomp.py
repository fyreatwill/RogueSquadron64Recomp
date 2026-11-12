#!/usr/bin/env python3
"""s7231 G1c: decompose gfx-task cost against what each task draws.

Input: owner-harness logs run with ROGUESQ_G1B=1 + ROGUESQ_G1CF=1. [g1cf] lines (one per VI: tasks, dsize = gfx task data
bytes, tri = RDP triangle commands forwarded, rt64tri) are binned into the second closed by the next [g1b] t=N line (stderr order).
Per flight second: tasks/s, sd_wall (mean gfx-task wall ms, from [g1b]), tri/task, dsize/task.
Prints, per log: the heavy window means (--t0/--t1), and a least-squares fit sd_wall = a + b*tri_k + c*dsize_k over flight seconds
(tri_k = tri/task in thousands, dsize_k = dsize/task in KB), with a shuffle control (seconds permuted: R^2 must collapse) and a
pooled fit over all logs. If one line fits both dd4 and dd6 seconds, the dd6 extra cost is explained by what is drawn (H-tris /
H-dl); if dd6 seconds sit above the pooled line at equal tri and dsize, the extra cost is per-primitive work that the counts
miss (H-clip).
Usage: s7231_cost_decomp.py log_a6.txt log_a4.txt [--t0 77 --t1 97 --flight0 60 --flight1 230]
"""
import re, sys, argparse, random
ap = argparse.ArgumentParser(); ap.add_argument('logs', nargs='+')
ap.add_argument('--t0', type=int, default=77); ap.add_argument('--t1', type=int, default=97)
ap.add_argument('--flight0', type=int, default=60); ap.add_argument('--flight1', type=int, default=230)
a = ap.parse_args()
G1B = re.compile(r'\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/')
G1CF = re.compile(r'\[g1cf\] vi=\d+ dd=(\d+) tasks=(\d+) dsize=(\d+) subs=(\d+) bytes=(\d+) tri=(\d+) rt64tri=(\d+)')

def load(path):
    rows = []; acc = [0, 0, 0, 0, 0]
    with open(path, errors='ignore') as f:
        for ln in f:
            m = G1CF.match(ln)
            if m:
                acc[0] += int(m[2]); acc[1] += int(m[3]); acc[2] += int(m[6]); acc[3] += int(m[7]); acc[4] += 1; continue
            m = G1B.match(ln)
            if m:
                t, tasks, sd = int(m[1]), int(m[3]), float(m[4])
                rows.append(dict(t=t, tasks=tasks, sd=sd, ctasks=acc[0], dsize=acc[1], tri=acc[2], rtri=acc[3], vis=acc[4]))
                acc = [0, 0, 0, 0, 0]
    return rows

def fit(X, y):
    # normal equations, tiny dense solve
    n = len(X[0]); A = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]; B = [sum(r[i] * v for r, v in zip(X, y)) for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda k: abs(A[k][i])); A[i], A[p] = A[p], A[i]; B[i], B[p] = B[p], B[i]
        if abs(A[i][i]) < 1e-12: return None, 0.0
        for k in range(n):
            if k != i:
                f = A[k][i] / A[i][i]; A[k] = [x - f * z for x, z in zip(A[k], A[i])]; B[k] -= f * B[i]
    c = [B[i] / A[i][i] for i in range(n)]
    my = sum(y) / len(y); ss = sum((v - my) ** 2 for v in y) or 1e-12
    res = sum((v - sum(ci * xi for ci, xi in zip(c, r))) ** 2 for r, v in zip(X, y))
    return c, 1 - res / ss

USE_DL = None  # set below: dsize is 0 on the owner path (g_rs64_g1cf_dsize not fed there), then the fit is sd = a + b*ktri
def feats(r):
    k = max(r['ctasks'], 1)
    return [1.0, r['tri'] / k / 1000.0] + ([r['dsize'] / k / 1024.0] if USE_DL else [])
def fmt(c): return f'{c[0]:.2f} + {c[1]:.3f}*ktri' + (f' + {c[2]:.3f}*KBdl' if USE_DL else '')

pool = []
USE_DL = any(r['dsize'] for p in a.logs for r in load(p))
for p in a.logs:
    rows = [r for r in load(p) if a.flight0 <= r['t'] <= a.flight1 and r['ctasks'] > 0]
    if not rows: print(p, 'no flight rows with [g1cf]'); continue
    w = [r for r in rows if a.t0 <= r['t'] < a.t1]
    mean = lambda L, f: sum(f(r) for r in L) / max(len(L), 1)
    print(f'== {p}: flight s={len(rows)}  window t={a.t0}-{a.t1} s={len(w)}')
    for name, L in (('window', w), ('flight', rows)):
        print(f'  {name:6s} tasks/s={mean(L, lambda r: r["tasks"]):.1f} sd_wall={mean(L, lambda r: r["sd"]):.2f} ms '
              f'tri/task={mean(L, lambda r: r["tri"] / r["ctasks"]):.0f} rt64tri/task={mean(L, lambda r: r["rtri"] / r["ctasks"]):.0f} '
              f'dsizeKB/task={mean(L, lambda r: r["dsize"] / r["ctasks"] / 1024):.1f}')
    X = [feats(r) for r in rows]; y = [r['sd'] for r in rows]
    c, r2 = fit(X, y)
    ys = y[:]; random.Random(7231).shuffle(ys); _, r2s = fit(X, ys)
    if c: print(f'  fit sd = {fmt(c)}  R2={r2:.3f}  (shuffle control R2={r2s:.3f})')
    pool += [(p, r) for r in rows]
if len(a.logs) > 1 and pool:
    X = [feats(r) for _, r in pool]; y = [r['sd'] for _, r in pool]; c, r2 = fit(X, y)
    print(f'== pooled fit sd = {fmt(c)}  R2={r2:.3f}')
    for p in a.logs:
        res = [r['sd'] - sum(ci * xi for ci, xi in zip(c, feats(r))) for q, r in pool if q == p]
        wres = [r['sd'] - sum(ci * xi for ci, xi in zip(c, feats(r))) for q, r in pool if q == p and a.t0 <= r['t'] < a.t1]
        if res: print(f'  residual {p}: flight mean {sum(res)/len(res):+.2f} ms, window mean {sum(wres)/max(len(wres),1):+.2f} ms')
