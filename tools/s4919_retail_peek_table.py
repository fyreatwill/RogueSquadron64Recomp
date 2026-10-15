#!/usr/bin/env python3
"""s4919: tabulate the hangar-gated retail producer-entry slot peek (s4918r oracle log).
Row bytes: [0:16]=arbiter 0x80128EA8..B7, so +6 is index 6, +7 index 7."""
import re, sys, collections
p = sys.argv[1] if len(sys.argv) > 1 else 'scratch/agent/s4918r/oracle.log'
txt = open(p).read()
arm = len(re.findall(r'\[phase-arm\]', txt))
m = re.search(r'slot-peek-summary pc=\S+ hits=(\d+)', txt)
print('phase-arm rows (control):', arm, ' gated hits:', m.group(1) if m else 'none')
c = collections.Counter()
for n, hx in re.findall(r'slot-peek-row n=(\d+) ((?:[0-9a-f]{2} ?){18})', txt):
    b = hx.split()
    c[(b[6], b[7], 'slot5' if '05' in b[:6] else 'no5')] += int(n)
for (p6, p7, s), n in sorted(c.items()):
    print(f'+6={p6} +7={p7} {s}: {n}')
tot = sum(c.values()); lt = sum(n for (a, b, _), n in c.items() if int(a, 16) < int(b, 16) - 1)
print(f'park-condition (+6 < +7-1) rows: {lt}/{tot}')
