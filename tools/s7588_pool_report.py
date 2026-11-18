#!/usr/bin/env python3
"""s7588 report: per arm log, [s7588-pool] main-queue block pool depth, backlog (enq-exec), plant alloc/dealloc; and [s7587-pool]
per-thread growth per begin. usage: s7588_pool_report.py log1 [log2 ...]"""
import re, sys
R = re.compile(r'\[s7588-pool\] where=(\w+) tid=(\d+) main=(\d) entries=(\d+) enq=(\d+) exec=(\d+) plantA=(\d+) plantD=(\d+) pool=(\d)')
P = re.compile(r'\[s7587-pool\] where=\w+ tid=(\d+) n=(\d+) .* entries=(\d+)')
for f in sys.argv[1:]:
    rows = [m.groups() for m in map(R.search, open(f, errors='replace')) if m]
    blk = [r for r in rows if r[0] == 'block']; post = [r for r in rows if r[0] == 'post']
    print(f'== {f}: {len(blk)} block samples, {len(post)} post samples, pool={rows[-1][8] if rows else "?"}')
    if blk:
        e = [int(r[3]) for r in blk]; b = [int(r[4]) - int(r[5]) for r in blk]
        print(f'  main entries first/max/last {e[0]}/{max(e)}/{e[-1]}  backlog max {max(b)}  last enq={blk[-1][4]} exec={blk[-1][5]} '
              f'plantA={blk[-1][6]} plantD={blk[-1][7]}')
    pt = {}
    for r in post: pt.setdefault(r[1], []).append((int(r[4]), int(r[3])))
    for t, v in sorted(pt.items()):
        sl = (v[-1][1] - v[0][1]) / max(1, v[-1][0] - v[0][0])
        print(f'  post tid {t}: {len(v)} samples entries first/last {v[0][1]}/{v[-1][1]} slope {sl:.4f}/post')
    th = {}
    for m in map(P.search, open(f, errors='replace')):
        if m: th.setdefault(m.group(1), []).append((int(m.group(2)), int(m.group(3))))
    for t, v in sorted(th.items()):
        if len(v) > 2:
            a, z = v[1], v[-1]; print(f'  s7587 tid {t}: {len(v)} samples, slope {(z[1]-a[1])/max(1,z[0]-a[0]):.4f}/begin')
