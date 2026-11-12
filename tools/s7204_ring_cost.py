#!/usr/bin/env python3
"""s7204 Retina flight cost: per arm, from ROGUESQ_PRESENT_RING Q rows restricted to wall t >= ring t0 + --from:
presents/s, gpu_ms median/p95/max, Q->Q gaps > 50 ms and > 250 ms; plus the [retina] swapchain row from the log.
usage: s7204_ring_cost.py DIR ARM... [--from 95]   (DIR holds ring_<ARM>.txt and log_<ARM>.txt)"""
import re, sys
a = sys.argv[1:]; frm = 95.0
if '--from' in a: i = a.index('--from'); frm = float(a[i+1]); del a[i:i+2]
d, arms = a[0], a[1:]
pc = lambda v, p: sorted(v)[int(p*(len(v)-1))] if v else 0
print('arm    swapchain              | n_q  pres/s gpu50 gpu95 gpumax | gap>50 gap>250 maxgap_ms')
for A in arms:
    sw = '?'
    try:
        for l in open(f'{d}/log_{A}.txt', 'rb'):
            if b'[retina] swapchain create' in l: sw = l.split(b'create ')[1].split()[0].decode()
    except OSError: pass
    T = []; G = []
    try:
        rows = [l.split() for l in open(f'{d}/ring_{A}.txt') if l.startswith('Q ')]
    except OSError: print(A, 'no ring'); continue
    if not rows: print(A, 'empty'); continue
    t0 = float(rows[0][1])
    for f in rows:
        t = float(f[1])
        if t - t0 < frm: continue
        T.append(t)
        m = [x for x in f if x.startswith('gpu_ms=')]
        if m: G.append(float(m[0][7:]))
    gaps = [(T[i+1]-T[i])*1000 for i in range(len(T)-1)]
    span = (T[-1]-T[0]) if len(T) > 1 else 1
    print(f'{A:6} {sw:22} | {len(T):5} {len(T)/span:6.1f} {pc(G,.5):5.2f} {pc(G,.95):5.2f} {max(G or [0]):6.2f} | '
          f'{sum(g>50 for g in gaps):6} {sum(g>250 for g in gaps):7} {max(gaps or [0]):8.1f}')
