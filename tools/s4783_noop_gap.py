#!/usr/bin/env python3
"""s4783: per musyxNoopStub window, count synth ticks between first rs_free and gate clear, and
how many mallocs/frees pass before the next synth tick after the clear (retail ordering)."""
import re
import sys

NM = {'8008ed00': 'ENTER', '8008ed44': 'CLEAR', '8009123c': 'SYNTH', '80001acc': 'MALLOC', '80001c98': 'FREE'}
ev = []
for line in open(sys.argv[1], errors='replace'):
    m = re.match(r'\[hit\] x addr=\S+ pc=0x([0-9a-f]+) .*?t=([\d.]+)s', line)
    if m:
        ev.append((NM.get(m.group(1), m.group(1)), float(m.group(2))))

for i, (n, t) in enumerate(ev):
    if n != 'ENTER':
        continue
    j = i
    while ev[j][0] != 'CLEAR':
        j += 1
    frees = [k for k in range(i, j) if ev[k][0] == 'FREE']
    k = j + 1
    while ev[k][0] != 'SYNTH':
        k += 1
    mal = sum(1 for q in range(j, k) if ev[q][0] == 'MALLOC')
    fr = sum(1 for q in range(j, k) if ev[q][0] == 'FREE')
    sy = sum(1 for q in range(frees[0], j) if ev[q][0] == 'SYNTH')
    print('ENTER t=%.2f firstFREE t=%.2f CLEAR t=%.2f nextSYNTH t=%.2f | synth between first free and clear: %d; mallocs=%d frees=%d before next synth'
          % (t, ev[frees[0]][1], ev[j][1], ev[k][1], sy, mal, fr))
