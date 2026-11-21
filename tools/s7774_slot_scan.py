#!/usr/bin/env python3
"""s7774: summarise [s7774] NPC-slot scans (ROGUESQ_S7774_SLOTS=1) per overlay swap.
Each swap = one pre line + one post line at the overlay window; the overlay identity comes from the [s7528] post idx line that
follows. Positive control: some tick line (in-mission) must show ovl>0. Verdict per mission-departing swap (pre ovl>0):
post ovl_unmapped>0 -> live slots with handlers a dispatch could no longer find (H-dormant / H-stale); 0 -> H-cleared.
rc 0 = control passed and a mission-departing swap was observed; rc 3 = control failed; rc 4 = no mission-departing swap."""
import re, sys
kv = lambda s: dict(re.findall(r'(\w+)=(\S+)', s))
rows, idx, ticks = [], [], []
for ln in open(sys.argv[1], errors='replace'):
    if ln.startswith('[s7774] '):
        d = kv(ln); (ticks if d['tag'] == 'tick' else rows).append(d)
    elif ln.startswith('[s7528] post'):
        idx.append(kv(ln).get('idx'))
ctl = max((int(t['ovl']) for t in ticks), default=0)
print(f'ticks={len(ticks)} tick_ovl_max={ctl} tick_live_max={max((int(t["live"]) for t in ticks), default=0)} swap_rows={len(rows)}')
dep = 0; stale = 0
for d in rows:
    print(f"  {d['tag']:4} ram={d['ram']} live={d['live']} objs={d['objs']} res={d['res']} ovl={d['ovl']} mapped={d['ovl_mapped']} "
          f"unmapped={d['ovl_unmapped']} first_unmapped={d['first_unmapped']} loaded={d['loaded']}")
for a, b in zip(rows, rows[1:]):
    if a['tag'] == 'pre' and b['tag'] == 'post' and int(a['ovl']) > 0:
        dep += 1; stale += int(b['ovl_unmapped'])
print(f'departing_swaps_with_ovl_handlers={dep} post_unmapped_total={stale} ctl={"PASS" if ctl > 0 else "FAIL"}')
sys.exit(3 if ctl == 0 else (4 if dep == 0 else 0))
