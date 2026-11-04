#!/usr/bin/env python3
"""s6877 G3: which mat3x4Multiply caller moves camera row 1, from [camcall2] rows (ROGUESQ_CAM_CALLER=1). Word 5 (pitch) is what the arms disagree on, and
the in-place site leaves it unchanged. Prints per caller: rows, sum|d w4|, sum|d w5|, largest w4 step, and the first ROWS rows that step word 4 by more than EPS.
Usage: g3_cam_calls.py run.log [ROWS] [EPS]"""
import re, sys
rows = int(sys.argv[2]) if len(sys.argv) > 2 else 8
eps = float(sys.argv[3]) if len(sys.argv) > 3 else 1e-5
by = {}; first = []
for ln in open(sys.argv[1], 'rb'):
    if not ln.startswith(b'[camcall2]'): continue
    m = re.search(rb'sw=(-?\d+) hra=(\w+) n=(\d+) .*was=(\S+) now=(\S+) A=\S+ B=\S+ pos=(\S+) d0=(\S+) e0=(\S+)', ln)
    if not m: continue
    was = [float(v) for v in m.group(4).split(b',')]; now = [float(v) for v in m.group(5).split(b',')]
    d4 = abs(now[1] - was[1]); d5 = abs(now[2] - was[2]); h = m.group(2).decode()
    b = by.setdefault(h, [0, 0.0, 0.0, 0.0]); b[0] += 1; b[1] += d4; b[2] += d5; b[3] = max(b[3], d4)
    if d4 > eps and len(first) < rows:
        first.append((int(m.group(1)), h, int(m.group(3)), was, now, m.group(6).decode()))
for h, b in sorted(by.items(), key=lambda kv: -kv[1][1]):
    print('hra=%s rows=%d sum|dw4|=%.6f sum|dw5|=%.6f max|dw4|=%.6f' % (h, b[0], b[1], b[2], b[3]))
for f in first:
    print('sw=%d hra=%s n=%d was=%s now=%s pos=%s' % f)
