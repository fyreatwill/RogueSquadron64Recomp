#!/usr/bin/env python3
"""s7919 G5c freeze-gap check on one ROGUESQ_PRESENT_RING file, with a same-run positive control.

usage: s7919_gap_check.py <ring[.zst]> [--thr-ms 250] [--plant-ms 300]
Reports (a) present gaps >= thr and (b) VI-origin holds >= thr (picture frozen while presents keep flowing), each with its
time from the first row, so a hold can be placed as load/boot vs flight. Control: a copy of the rows with one planted gap of
plant-ms in the middle (all later stamps shifted) and one planted VI hold of plant-ms must each be detected, else the
instrument is blind and the result is void (exit 3).
"""
import sys, argparse, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent'))
from ring_stalls import rows

def scan(Q, thr):
    gaps = [(t0 - Q[0][0], (t1 - t0) * 1e3) for (t0, _), (t1, _) in zip(Q, Q[1:]) if (t1 - t0) * 1e3 >= thr]
    holds = []; s, v = Q[0]
    for t, vi in Q[1:]:
        if vi != v:
            if (t - s) * 1e3 >= thr: holds.append((s - Q[0][0], (t - s) * 1e3))
            s, v = t, vi
    return gaps, holds

ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--thr-ms', type=float, default=250)
ap.add_argument('--plant-ms', type=float, default=300); a = ap.parse_args()
Q = list(rows(a.ring))
if len(Q) < 100: print('rows=%d too few -> void' % len(Q)); sys.exit(3)
g, h = scan(Q, a.thr_ms)
m = len(Q) // 2; d = a.plant_ms / 1e3
# control 1: planted present gap
P = Q[:m] + [(t + d, vi) for t, vi in Q[m:]]
pg, _ = scan(P, a.thr_ms); c1 = any(abs(x - (Q[m - 1][0] - Q[0][0])) < 1e-6 for x, _ in pg)
# control 2: planted VI hold (rows over plant-ms after the midpoint all show the midpoint's origin, then it changes)
t0 = Q[m][0]; H = [(t, Q[m][1] if t0 <= t < t0 + d else vi) for t, vi in Q]
H = [(t, vi) for t, vi in H]; _, ph = scan(H, a.thr_ms); c2 = len(ph) > len(h)
dur = Q[-1][0] - Q[0][0]
print('rows=%d dur_s=%.1f max_gap_ms=%.0f gaps_ge_thr=%d holds_ge_thr=%d control_gap=%s control_hold=%s' % (
    len(Q), dur, max((t1 - t0) * 1e3 for (t0, _), (t1, _) in zip(Q, Q[1:])), len(g), len(h), c1, c2))
for x, ms in g: print('  GAP  at %7.1f s  %7.0f ms' % (x, ms))
for x, ms in h: print('  HOLD at %7.1f s  %7.0f ms' % (x, ms))
sys.exit(0 if (c1 and c2) else 3)
