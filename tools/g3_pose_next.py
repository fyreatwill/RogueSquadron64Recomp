#!/usr/bin/env python3
"""s6876 G3: POSE_FREEZE x list that lands N ticks after an arm's freezes. Takes the [posefreeze] rows of a 60 Hz limiter arm (one tick per VI)
and adds N ticks of x, one tick being dx / (dvi - freeze VIs) between the first two freezes. [camlog] cannot give it: on lvl10 its rows stop
before flight with a stale pointer (s6876). Needs two freezes on a straight stretch.
Usage: g3_pose_next.py run.log N   (N = 0.5 for the next tick, 1.5 for the one after)"""
import re, sys

n, rows = float(sys.argv[2]), []
for ln in open(sys.argv[1], 'rb'):
    if ln.startswith(b'[posefreeze]'):
        m = re.search(rb'vi=(\d+) pos=([-\d.]+),.* ms=(\d+)', ln)
        rows.append((int(m.group(1)), float(m.group(2)), int(m.group(3))))
(v0, x0, ms), (v1, x1, _) = rows[0], rows[1]
tick = (x1 - x0) / (v1 - v0 - ms * 60 / 1000)
print(' '.join('%.3f' % (r[1] + n * tick) for r in rows))
