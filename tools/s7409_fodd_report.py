#!/usr/bin/env python3
"""s7409 class BS report over a build_fodd run log (last [s7409-dump] block).
CONTROL PASS: planted f_odd swaps were taken (plant>0) and every one was flagged (plant_bad == plant), and the live
status_w probes after an OR saw FR=1 on every call (the probe sees real mode flips).
VERDICT H-consistent: every probe with an expectation saw that mode on every call (bad=0), and the odd view always wrote
the slot its mode says (view_bad=0). H-fr-leak: an FR=0 entry saw FR=1 (or the reverse). rc 0 only for PASS+consistent.
Usage: s7409_fodd_report.py <log>"""
import re, sys
txt = open(sys.argv[1], errors='replace').read().split('\n')
starts = [i for i, l in enumerate(txt) if '[s7409-dump]' in l]
if not starts: print('NO DUMP'); sys.exit(2)
rows = []
for l in txt[starts[-1] + 1:]:
    if '[s7409-site]' not in l:
        if '[s7409-dump]' in l: break
        continue
    d = dict(re.findall(r'(\w+)=(\S+)', l)); rows.append(d)
I = lambda d, k: int(d[k])
pl = sum(I(d, 'plant') for d in rows); plb = sum(I(d, 'plant_bad') for d in rows)
flips = [d for d in rows if d['where'] == 'status_w' and d['expect'] == '1']
flip_ok = flips and all(I(d, 'calls') > 0 and I(d, 'm1') == I(d, 'calls') for d in flips)
bad = [d for d in rows if d['expect'] != '-1' and I(d, 'bad')]
vbad = [d for d in rows if I(d, 'view_bad')]
for d in rows:
    print(f"ROW {d['fn']:32s} {d['where']:8s} exp={d['expect']:>2s} calls={d['calls']:>10s} m0={d['m0']:>10s} m1={d['m1']:>10s} "
          f"bad={d['bad']} view_bad={d['view_bad']} plant={d['plant_bad']}/{d['plant']}")
ctl = pl > 0 and plb == pl and flip_ok
cons = not bad and not vbad
print(f"dumps={len(starts)} sites={len(rows)} plant={plb}/{pl} flip_sites={len(flips)} flip_ok={bool(flip_ok)}")
print('CONTROL', 'PASS' if ctl else 'FAIL')
print('VERDICT', 'H-consistent' if cons else 'H-fr-leak' if bad else 'H-view-mismatch',
      ' '.join(f"{d['fn']}:{d['where']}" for d in bad + vbad)[:300])
sys.exit(0 if ctl and cons else 1)
