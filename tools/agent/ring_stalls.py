#!/usr/bin/env python3
"""s7458 class DN: stall score of a ROGUESQ_PRESENT_RING file (lib/rt64 plume_metal.cpp ~2075, rt64_present_queue.cpp Q rows).

usage: ring_stalls.py <ring[.zst]> [gap_s=30] [--end-wall <epoch_s>]
prints: vi_stalls30s=<n> max_gap_ms=<m> max_vihold_ms=<h> tail_ms=<t> rows=<r>     (rows=0 -> vi_stalls30s=na)

A stall episode is any interval >= gap_s in which EITHER
  (a) no Q (present) row was written           -> the present path itself stopped (H-ring), or
  (b) Q rows kept coming but vi= (the VI origin the present showed) never changed -> the guest stopped swapping while the
      host re-presented the same frame (H-blind: a pure present-gap count misses this one).
Overlapping intervals are merged into one episode. --end-wall: the wall time the launcher saw the game still alive just
before SIGKILL; (end_wall - ring mtime) is the silent tail after the last flushed row (rows flush every 64, ~0.5 s), and a
tail >= gap_s is one more episode (a hung game writes nothing, so (a) alone could never see it). Pass it only for arms that
were alive at the end: a dead game's silent tail is a death, not a stall.
"""
import os, subprocess, sys

def rows(path):
    if path.endswith('.zst'):
        data = subprocess.run(['zstd', '-dc', path], capture_output=True).stdout.decode('latin-1')
    else:
        data = open(path, encoding='latin-1').read()
    for l in data.split('\n')[:-1]:       # a SIGKILLed ring may end mid-line: the element after the last '\n' is dropped
        if l.startswith('Q ') and ' vi=' in l:
            p = l.split()
            try:
                t = float(p[1]); vi = next(x[3:] for x in p if x.startswith('vi='))
            except (ValueError, StopIteration):
                continue
            yield t, vi

def score(path, gap_s=30.0, end_wall=None):
    Q = list(rows(path))
    if not Q:
        return dict(n='na', gap=0, hold=0, tail=0, rows=0)
    iv = []; mg = 0.0; mh = 0.0
    for (t0, _), (t1, _) in zip(Q, Q[1:]):
        g = t1 - t0; mg = max(mg, g)
        if g >= gap_s: iv.append((t0, t1))
    s, v = Q[0]
    for t, x in Q[1:] + [(Q[-1][0], None)]:
        if x != v:
            h = t - s; mh = max(mh, h)
            if h >= gap_s: iv.append((s, t))
            s, v = t, x
    iv.sort(); n = 0; ce = None
    for a, b in iv:
        if ce is None or a > ce: n += 1; ce = b
        else: ce = max(ce, b)
    tail = 0.0
    if end_wall is not None:
        tail = max(0.0, end_wall - os.path.getmtime(path))
        if tail >= gap_s: n += 1
    return dict(n=n, gap=mg * 1e3, hold=mh * 1e3, tail=tail * 1e3, rows=len(Q))

if __name__ == '__main__':
    a = sys.argv[1:]; ew = None
    if '--end-wall' in a:
        i = a.index('--end-wall'); ew = float(a[i + 1]); del a[i:i + 2]
    if not a:
        sys.exit(__doc__)
    gap = float(a[1]) if len(a) > 1 else 30.0
    if not os.path.exists(a[0]):
        print('vi_stalls30s=na max_gap_ms=0 max_vihold_ms=0 tail_ms=0 rows=0'); sys.exit(0)
    r = score(a[0], gap, ew)
    print(f"vi_stalls30s={r['n']} max_gap_ms={r['gap']:.0f} max_vihold_ms={r['hold']:.0f} tail_ms={r['tail']:.0f} rows={r['rows']}")
