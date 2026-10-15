#!/usr/bin/env python3
"""s4918: producer-entry slot bytes vs commit outcome. Usage: s4918_table.py run.log
For each 'bProd-entry' mark, take bytes +0..+7 and the next same-tid 'sb pc=8001BDFC' (parked, state 3)
or 'sb pc=8001BE30' (committed, state 4). Prints counts keyed by (outcome, bytes)."""
import re, sys
from collections import Counter
R = re.compile(r'\[s4913\] k=(\d+) t=([\d.]+) tid=(\d+) (.+?) A=(\d+) B=(\d+) ?(.*)$')
pending, c, cb = {}, Counter(), Counter()
for ln in open(sys.argv[1], errors='replace'):
    m = R.match(ln)
    if not m: continue
    tid, tag, slots = m.group(3), m.group(4), m.group(7).split()
    if tag == 'bProd-entry': pending[tid] = slots[:8]
    elif tag.startswith('sb pc=8001BDFC') or tag.startswith('sb pc=8001BE30'):
        if tid in pending:
            o = '3-park' if 'BDFC' in tag else '4-commit'
            c[o] += 1; cb[(o, ' '.join(pending.pop(tid)))] += 1
print(dict(c))
for (o, b), n in sorted(cb.items(), key=lambda x: -x[1])[:25]: print(n, o, 'bytes+0..7:', b)
