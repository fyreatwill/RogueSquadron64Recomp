#!/usr/bin/env python3
"""s4915: per-waitForPostSwapAck-call table. Usage: s4915_table.py run.log
Groups each call (recv-ack count) by the psrr/BF20 events observed during it, plus slot-bytes at a ret-0."""
import re, sys
from collections import Counter

ev = []
for l in open(sys.argv[1]):
    m = re.match(r'\[s4913\] k=(\d+) t=([\d.]+) tid=(\d+) (\S+) A=(\d) B=(\d) ?(.*)', l)
    if m:
        ev.append((int(m[1]), float(m[2]), int(m[3]), m[4], int(m[5]), m[7].strip()))

calls, cur = [], None
for e in ev:
    tag = e[3]
    if tag == 'waitForPostSwapAck':
        cur = dict(recv=0, psrr=[], t=e[1]); calls.append(cur)
    elif cur is not None:
        if tag == 'recv-ack':
            cur['recv'] += 1
        elif tag.startswith('psrr'):
            cur['psrr'].append((tag, cur['recv'], e[5]))

c = Counter()
for x in calls:
    c[(x['recv'], tuple((p[0], p[1]) for p in x['psrr']))] += 1
print("calls:", len(calls))
for k, v in c.most_common(15):
    print(v, k)
print("--- slot bytes at each ret-0 (first 6):")
n = 0
for x in calls:
    for p in x['psrr']:
        if p[0] == 'psrr-bf20-ret-0' and n < 6:
            print(x['recv'], p[2]); n += 1
