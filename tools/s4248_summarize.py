#!/usr/bin/env python3
"""Bucket [s4248] per-audio-task lines (wall, lock-wait, thread-CPU time, DMA volume) into 3 s windows."""
import re, sys, collections

b = collections.defaultdict(list)
pat = re.compile(r'\[s4248\] t=([\d.]+) wall_us=(\d+) lockwait_us=(\d+) cpu_us=(\d+) data_size=(\d+) '
                 r'rd_bytes=(\d+) rd_calls=(\d+) wr_bytes=(\d+) wr_calls=(\d+)')
for line in open(sys.argv[1], errors='ignore'):
    m = pat.match(line)
    if m:
        v = [float(x) for x in m.groups()]
        b[int(v[0]) // 3 * 3].append(v)
for k in sorted(b):
    r = b[k]
    n = len(r)
    a = lambda i: sum(x[i] for x in r) / n
    print(f"t={k:3d} n={n:3d} wall={a(1):8.0f} lockwait={a(2):8.0f} cpu={a(3):6.0f} "
          f"maxwall={max(x[1] for x in r):8.0f} maxlock={max(x[2] for x in r):8.0f} rdB={a(5):7.0f}")
