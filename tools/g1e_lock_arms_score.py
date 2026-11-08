#!/usr/bin/env python3
"""s6969 G1e: score a ROGUESQ_VI_LOCK / PRESENT_DRAIN_ACQ arm table from present rings (ROGUESQ_PRESENT_RING), one row per arm.
Per arm, over [--from, end): W phase p50 (ms after the display vsync; grid fitted from P 'at'), Q phase p50, share of presents at
level (acq > --lvl ms), lat p50/p90 (P - Q + tp), misses/s (shown P->P >= 25 ms), drain drops (D rows), level entries (hysteresis:
enter after --minrun consecutive presents with acq > --lvl, leave after --minrun below) and the time at level per entry.
Control: a locked arm must show W p50 within 1.5 ms of --target (else LOCK did not engage); an unlocked arm says 'free'.
usage: g1e_lock_arms_score.py name=ring.txt [name=ring.txt ...] [--from 95] [--lvl 5] [--minrun 30] [--target 10] [--slow 30] [--locked n1,n2]
slow% = presents with latency > --slow ms: catches shallow levels (16:9 s6970: ACQ8-alone 36 ms episodes at acq<5 that lvl% misses)."""
import argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('rings', nargs='+')
for k, v in (('from', 95.0), ('lvl', 5.0), ('target', 10.0), ('slow', 30.0)): ap.add_argument('--' + k, dest=k.replace('from', 'frm'), type=float, default=v)
ap.add_argument('--minrun', type=int, default=30); ap.add_argument('--locked', default=''); a = ap.parse_args()
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
locked = set(x for x in a.locked.split(',') if x)
print(f"{'arm':6} | {'span s':>9} | {'W p50':>5} {'Q p50':>5} | {'lvl%':>5} | {'lat p50/p90':>11} | slow% | miss/s | drops | entries (t s, dur s)")
for spec in a.rings:
    name, path = spec.split('=', 1); W = []; Q = []; P = {}; D = []; t0 = None
    for l in open(path, errors='replace'):
        p = l.split()
        if len(p) < 2 or not l.endswith('\n'): continue
        kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
        try:
            t = float(p[1]); t0 = t if t0 is None else t0; t -= t0
            if p[0] == 'W': W.append(t)
            elif p[0] == 'D': D.append(t)
            elif p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv: Q.append((t, float(kv['acq_ms']), kv['mtl'], float(kv['tp_ms'])))
            elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P[kv['mtl']] = float(kv['at']) - t0
        except (KeyError, ValueError): pass
    ps = sorted(v for v in P.values() if v > a.frm)
    if len(ps) < 100: print(f"{name:6} | too few presents ({len(ps)})"); continue
    Td = 1 / 60; k = [0]
    for i in range(1, len(ps)): k.append(k[-1] + max(1, round((ps[i] - ps[i - 1]) / Td)))
    mk = st.mean(k); mt = st.mean(ps); Td = sum((x - mk) * (y - mt) for x, y in zip(k, ps)) / sum((x - mk) ** 2 for x in k); ref = mt - Td * mk
    ph = lambda t: ((t - ref) / Td % 1) * Td * 1e3
    end = ps[-1]; q = [x for x in Q if a.frm <= x[0] <= end and x[2] in P]
    w = [ph(t) for t in W if a.frm <= t <= end]; acq = [x[1] for x in q]
    lat = [(P[x[2]] - x[0]) * 1e3 + x[3] for x in q]
    shown = sorted(P[x[2]] for x in q); miss = sum(1 for u, v in zip(shown, shown[1:]) if v - u >= 0.025)
    # level state with hysteresis: enter after --minrun consecutive presents with acq > --lvl, leave after --minrun consecutive below
    hi = [x > a.lvl for x in acq]; ent = []; lv_on = False; run = 0; start = 0
    for i, h in enumerate(hi):
        if h != lv_on: run += 1
        else: run = 0
        if run >= a.minrun:
            j = i - a.minrun + 1
            if not lv_on: start = q[j][0]
            else: ent.append((start, q[j][0] - start))
            lv_on = not lv_on; run = 0
    if lv_on: ent.append((start, q[-1][0] - start))
    wp = pc(w, .5); ctl = ('ENGAGED' if abs(wp - a.target) < 1.5 else 'NOT-ENGAGED') if name in locked else 'free'
    lv = 100 * sum(hi) / len(hi) if hi else float('nan'); dr = sum(1 for t in D if a.frm <= t <= end)
    es = ' '.join(f"{t:.0f}({d:.0f})" for t, d in ent) or '-'
    print(f"{name:6} | {a.frm:4.0f}-{end:4.0f} | {wp:5.1f} {pc([ph(x[0]) for x in q], .5):5.1f} | {lv:5.1f} | {pc(lat, .5):5.1f} {pc(lat, .9):5.1f} | {100 * sum(x > a.slow for x in lat) / max(1, len(lat)):5.1f} | {miss / (end - a.frm):6.3f} | {dr:5d} | {len(ent)}: {es}  [{ctl}]")
