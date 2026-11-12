#!/usr/bin/env python3
"""s7208: per-10 s window of a ROGUESQ_PRESENT_RING file: Q presents (skip=0), back-to-back pairs (< 4 ms, both skip=0),
and the pair kind (V = VI-path present wl_ms==0, E = early present wl_ms>0).
usage: s7208_present_pairs.py ring.txt [ring2.txt ...]"""
import sys, collections
for fn in sys.argv[1:]:
    Q = []
    for l in open(fn):
        if l.startswith('Q '):
            p = l.split(); kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
            if kv.get('skip') == '0':
                Q.append((float(p[1]), 'E' if float(kv.get('wl_ms', '0')) > 0 else 'V', kv.get('vi', '?')))
    t0 = Q[0][0]; tot = collections.Counter(); pr = collections.Counter(); kinds = collections.Counter()
    for i, (t, k, vi) in enumerate(Q):
        s = int((t - t0) / 10) * 10; tot[s] += 1
        if i and (t - Q[i - 1][0]) * 1000 < 4: pr[s] += 1; kinds[Q[i - 1][1] + k] += 1
    print(fn, 'presents', len(Q), 'pairs', sum(pr.values()), dict(kinds))
    print('  win(s):presents/pairs ' + ' '.join(f'{s}:{tot[s]}/{pr[s]}' for s in sorted(tot)))
