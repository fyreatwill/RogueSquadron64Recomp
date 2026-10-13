#!/usr/bin/env python3
"""s4783: order oracle hits inside each musyxNoopStub (0x8008ED00) window up to the gate clear (0x8008ED44)."""
import re
import sys
from collections import Counter

NAMES = {'8008ed00': 'ENTER', '8008ed14': 'GATEPATH', '8008ed44': 'CLEAR',
         '80091eb0': 'WAITFN', '8009123c': 'SYNTH', '80001acc': 'MALLOC', '80001c98': 'FREE'}

ev = []
for line in open(sys.argv[1], errors='replace'):
    m = re.match(r'\[hit\] (\w) addr=(0x[0-9a-f]+) pc=0x([0-9a-f]+) .*?t=([\d.]+)s', line)
    if not m:
        continue
    kind, _addr, pc, t = m.groups()
    if kind == 'w':
        ev.append(('GATEWR@' + pc, t, ''))
    elif pc in NAMES:
        a0 = re.search(r' a0=(0x[0-9a-f]+)', line)
        ev.append((NAMES[pc], t, a0.group(1) if a0 else ''))

print('totals', dict(Counter(e[0] for e in ev)))
win = None
wins = []
for name, t, x in ev:
    if name == 'ENTER':
        win = {'t': t, 'ev': []}
        wins.append(win)
    elif win is not None:
        win['ev'].append((name, x))
        if name == 'CLEAR':
            win = None
for w in wins:
    c = Counter(n for n, _ in w['ev'])
    seq = []
    for n, x in w['ev']:
        if seq and seq[-1][0] == n:
            seq[-1][1] += 1
        else:
            seq.append([n, 1, x])
    print('WIN t=%s' % w['t'], dict(c))
    print('   ', ' '.join('%s*%d%s' % (n, k, '(%s)' % x if n == 'MALLOC' and x else '') for n, k, x in seq[:40]))

# s4783 part 2: what follows each CLEAR (synth ticks / mallocs after the free burst)
print('--- after CLEAR')
idx = [i for i, e in enumerate(ev) if e[0] == 'CLEAR']
for i in idx:
    seq = []
    for n, x_t, x in ev[i + 1:i + 400]:
        if n.startswith('GATEWR'):
            n = n[:6]
        if seq and seq[-1][0] == n:
            seq[-1][1] += 1
        else:
            seq.append([n, 1, x])
    print('CLEAR t=%s next:' % ev[i][1], ' '.join('%s*%d%s' % (n, k, '(%s)' % x if n == 'MALLOC' and x else '') for n, k, x in seq[:12]))
