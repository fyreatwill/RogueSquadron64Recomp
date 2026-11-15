#!/usr/bin/env python3
"""s7410 class BT report over a build_fsv run log (last [s7410-dump] block).
CONTROL PASS: planted post-restore flips of f24 and s1 were taken (plant>0) and every one was flagged (plant_bad == plant).
VERDICT H-preserved: every return of every probed routine left f20..f30 (.u64), s0-s8 and sp equal to entry and FR mode
equal to entry (fbad=gbad=mbad=0). H-clobber-live: a returned call changed one of them. odd_changed is informational (the
FR=1 own odd slots are invisible to an FR=0 caller in the recomp layout). rc 0 only for PASS + preserved.
Usage: s7410_fsv_report.py <log>"""
import re, sys
txt = open(sys.argv[1], errors='replace').read().split('\n')
starts = [i for i, l in enumerate(txt) if '[s7410-dump]' in l]
if not starts: print('NO DUMP'); sys.exit(2)
rows = []
for l in txt[starts[-1] + 1:]:
    if '[s7410-site]' not in l:
        if '[s7410-dump]' in l: break
        continue
    rows.append(dict(re.findall(r'(\w+)=(\S+)', l)))
I = lambda d, k: int(d[k], 0)
for d in rows:
    print(f"ROW {d['fn']:30s} rets={d['rets']:>10s} m1_entry={d['m1_entry']:>8s} fbad={d['fbad']} fmask={d['fmask']} gbad={d['gbad']} "
          f"gmask={d['gmask']} mbad={d['mbad']} odd_changed={d['odd_changed']} plant={d['plant_bad']}/{d['plant']}")
pl = sum(I(d, 'plant') for d in rows); plb = sum(I(d, 'plant_bad') for d in rows)
bad = [d['fn'] for d in rows if I(d, 'fbad') or I(d, 'gbad') or I(d, 'mbad')]
ctl = pl > 0 and plb == pl
print(f"dumps={len(starts)} sites={len(rows)} plant={plb}/{pl}")
print('CONTROL', 'PASS' if ctl else 'FAIL')
print('VERDICT', 'H-preserved' if not bad else 'H-clobber-live ' + ','.join(bad))
sys.exit(0 if ctl and not bad else 1)
