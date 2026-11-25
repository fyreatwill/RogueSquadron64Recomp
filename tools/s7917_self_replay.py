#!/usr/bin/env python3
"""s7917 G3 m6 island B: ROGUESQ_RAND_REPLAY table from a PORT arm's own ROGUESQ_RAND_TRACE (not a retail oracle log, s7896).
Rows 'idx vi site seed' (column 4 = rngSeed before the call, src/main/rt64_render_context.cpp rs64_rand_trace); marker/probe rows
(the s7916_rand_site_cmp.py MARKS set, non-0x80 sites, rows with extra fields) are dropped; stops at the first 0x800FA730 mission
tick because the replay only acts pre-tick. Writes "SITE ORD SEED" (as s7896_rand_replay.py). Checks the LCG seed' = seed*0xA8351D63
on consecutive kept rows (rc 3 on any break: the filter dropped or kept a wrong row).
--drop SITE[,SITE]: omit that site's rows (negative-control table). usage: s7917_self_replay.py TRACE OUT [--drop 8006c0fc]"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen
MARKS = {0x800027C0, 0x8006BEC8, 0x8006C018, 0x8006C010, 0x800AF374, 0x800C6674, 0x8008EE08, 0x8008EE84,
         0x800989D8, 0x80098DE0, 0x80099720, 0x800998E8, 0x800FA730,
         0x800B3FA0, 0x800B380C, 0x800B4004}  # s7917: XTRACE_MEM marker rows of the 4-field shape (own idx counter)
a = sys.argv[1:]; drop = set()
if '--drop' in a: i = a.index('--drop'); drop = {int(x, 16) for x in a[i + 1].split(',')}; del a[i:i + 2]
if len(a) != 2: print(__doc__); sys.exit(2)
rows, ordn, vi_end = [], collections.Counter(), None
for l in zopen(a[0]):
    f = l.split()
    if len(f) < 4: continue
    s = int(f[2], 16)
    if s == 0x800FA730: vi_end = int(f[1]); break
    if len(f) != 4 or s in MARKS or s >> 24 != 0x80: continue
    ordn[s] += 1; rows.append((s, ordn[s], int(f[3], 16)))
bad = sum(1 for i in range(len(rows) - 1) if rows[i + 1][2] != rows[i][2] * 0xA8351D63 % (1 << 32))
kept = [r for r in rows if r[0] not in drop]
with open(a[1], 'w') as o:
    for s, k, v in kept: o.write('%08x %d %08x\n' % (s, k, v))
print(f'{len(rows)} pre-tick rand rows ({len(kept)} written, {len(rows) - len(kept)} dropped), {len(ordn)} sites, first tick VI {vi_end}, LCG breaks {bad}')
sys.exit(3 if bad or not rows or vi_end is None else 0)
