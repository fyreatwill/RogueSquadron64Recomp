#!/usr/bin/env python3
"""s4785: per musyxNoopStub gate clear in the s4783 retail oracle log, the callers (ra) of the rs_mallocs that run
before the next synth tick, and the last one -- the guest point where audio re-init ends."""
import collections
import re
import sys

ev = []
for line in open(sys.argv[1], errors='replace'):
    m = re.match(r'\[hit\] x addr=\S+ pc=0x([0-9a-f]+) .*?t=([\d.]+)s.*? ra=0x([0-9a-f]+)', line)
    if m:
        ev.append((m.group(1), float(m.group(2)), m.group(3)))
for i, (p, t, ra) in enumerate(ev):
    if p != '8008ed44':
        continue
    k = i + 1
    while ev[k][0] != '8009123c':
        k += 1
    ms = [ev[q] for q in range(i, k) if ev[q][0] == '80001acc']
    c = collections.Counter(x[2] for x in ms)
    print('clear t=%.2f n_malloc=%d last_ra=%s next_synth t=%.2f hist=%s'
          % (t, len(ms), ms[-1][2] if ms else None, ev[k][1], dict(c)))
