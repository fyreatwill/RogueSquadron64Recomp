#!/usr/bin/env python3
"""s7694 G5c freeze scan of a ROGUESQ_PRESENT_RING: every present gap and every VI-origin hold >= thr ms, with t relative
to the first row. usage: s7694_freeze_scan.py <ring> [thr_ms=250] [--ctl <epoch_s>]
--ctl: epoch wall time a deliberate SIGSTOP was applied (positive control); the event nearest it within 3 s is labelled CTL."""
import sys
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), 'agent'))
from ring_stalls import rows
a = sys.argv[1:]; ctl = None
if '--ctl' in a: i = a.index('--ctl'); ctl = float(a[i+1]); del a[i:i+2]
ring = a[0]; thr = float(a[1]) / 1000 if len(a) > 1 else 0.25
R = list(rows(ring))
if not R: print('rows=0'); sys.exit(1)
t0 = R[0][0]; ev = []
if ctl is not None:  # ring clock is host monotonic, ctl is epoch: map via ring mtime ~ last row (rows flush every 64, ~0.5 s)
    ctl = ctl - __import__('os').path.getmtime(ring) + R[-1][0]
pt, pv, hs = R[0][0], R[0][1], R[0][0]
for t, vi in R[1:]:
    if t - pt >= thr: ev.append(('gap', pt, t - pt))
    if vi != pv:
        if pt - hs >= thr: ev.append(('vihold', hs, pt - hs))
        hs = t
    pt, pv = t, vi
if pt - hs >= thr: ev.append(('vihold', hs, pt - hs))
ctlhit = 0
for k, s, d in sorted(ev, key=lambda e: e[1]):
    lab = ''
    if ctl is not None and abs(s - ctl) < 3: lab = ' CTL'; ctlhit += 1
    print(f'{k} t={s - t0:8.2f}s dur={d * 1000:8.1f}ms{lab}')
nc = [e for e in ev if not (ctl is not None and abs(e[1] - ctl) < 3)]
print(f'summary rows={len(R)} span_s={pt - t0:.1f} events={len(ev)} noctl_events={len(nc)} '
      f'noctl_after95={sum(1 for e in nc if e[1] - t0 > 95)} ctl_hit={ctlhit if ctl is not None else "na"}')
