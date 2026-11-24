#!/usr/bin/env python3
"""s7896 G3 island B: retail pre-tick rand table for ROGUESQ_RAND_REPLAY (src/main/rt64_render_context.cpp).
Reads a det_pair retail oracle log (rs64_oracle --exec-trace 0x80003430:...:0x80003470 rows: RA, seed-before) and writes one
"SITE ORD SEED" row per rand call before the first mission tick (0x800FA730): SITE = jal address (RA - 8, the port's
rs64_rand_site), ORD = 1-based ordinal of calls from that SITE, SEED = rngSeed before the call. The port then gives the ORD-th
call from SITE retail's seed, so per-site value streams match retail even where other sites' call counts differ.
rand is seed' = seed * 0xA8351D63 (returned); the script checks that on every consecutive retail pair (rc 3 on a break: the
log is not a complete rand trace). usage: s7896_rand_replay.py ORACLE_LOG OUT [--burst GAP]
s7900: --burst GAP writes "SITE BURST BORD SEED" instead: a site's calls split into bursts at silences > GAP VI (retail VI from
the oracle's [vi] t= lines, 1 s resolution), BORD = ordinal within the burst. The port reads it with ROGUESQ_RAND_REPLAY_BURST=GAP
(same GAP), so a scene that runs longer on one side (e.g. the attract flame phase, s7900) does not shift later bursts' values."""
import sys, collections
GAP = int(sys.argv[sys.argv.index('--burst') + 1]) if '--burst' in sys.argv else 0
if GAP: del sys.argv[sys.argv.index('--burst'):sys.argv.index('--burst') + 2]
if len(sys.argv) != 3: print(__doc__); sys.exit(2)
import re
vi = 0; last = {}; bno = collections.Counter(); bord = collections.Counter()
rows, ordn = [], collections.Counter()
for l in open(sys.argv[1], errors='replace'):
    if l.startswith('[vi] t='):
        m = re.search(r' vi=(\d+)', l); vi = int(m.group(1)) if m else vi; continue
    if not l.startswith('[xtrace] '): continue
    h = l[:120]
    if 'pc=800fa730' in h: break
    f = h.split()[1:]
    if len(f) > 4 and f[4] == 'pc=80003430':
        site = int(f[2], 16) - 8; ordn[site] += 1
        if GAP:
            if site in last and vi - last[site] > GAP: bno[site] += 1; bord[site] = 0
            last[site] = vi; bord[site] += 1; rows.append((site, (bno[site], bord[site]), int(f[3], 16)))
        else: rows.append((site, ordn[site], int(f[3], 16)))
bad = sum(1 for i in range(len(rows) - 1) if rows[i + 1][2] != rows[i][2] * 0xA8351D63 % (1 << 32))
with open(sys.argv[2], 'w') as o:
    for s, k, v in rows: o.write(('%08x %d %d %08x\n' % (s, k[0], k[1], v)) if GAP else ('%08x %d %08x\n' % (s, k, v)))
print(f'{len(rows)} pre-tick rand rows, {len(ordn)} sites, LCG breaks {bad}')
sys.exit(3 if bad or not rows else 0)
