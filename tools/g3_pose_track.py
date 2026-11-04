#!/usr/bin/env python3
"""s6876 G3: pick POSE_FREEZE x values from a no-input scout run. POSE_FREEZE fires when x first reaches each value, so only new
maxima of x are usable. Reads [poselock] rows, prints the track, then the longest stretches where x sets new maxima with little
heading change (straight flight), with evenly spaced x candidates inside them.
Usage: g3_pose_track.py run.log [n_candidates]"""
import math, re, sys

pts = []
for ln in open(sys.argv[1], 'rb'):
    if ln.startswith(b'[poselock] n='):
        m = re.match(rb'\[poselock\] n=(\d+) pos=([-\d.]+),([-\d.]+),([-\d.]+)', ln)
        if m:
            pts.append((int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))))
want = int(sys.argv[2]) if len(sys.argv) > 2 else 3
print('rows', len(pts))
for p in pts[::max(1, len(pts) // 16)]:
    print('  n=%d x %.2f y %.2f z %.2f' % p)
best, cur, top = [], [], -1e30
for a, b in zip(pts, pts[1:]):
    h = math.atan2(b[3] - a[3], b[1] - a[1])
    if b[1] > top and b[1] > a[1] and (not cur or abs(math.remainder(h - cur[0][1], math.tau)) < 0.15):
        cur.append((b, h)); top = b[1]
    else:
        if len(cur) > len(best):
            best = cur
        cur = []; top = max(top, b[1])
if len(cur) > len(best):
    best = cur
if len(best) < want + 1:
    print('no straight rising stretch'); sys.exit(1)
x0, x1 = best[0][0][1], best[-1][0][1]
print('stretch n=%d..%d x %.2f..%.2f heading %.3f' % (best[0][0][0], best[-1][0][0], x0, x1, best[0][1]))
print('FZ="%s"' % ' '.join('%.2f' % (x0 + (x1 - x0) * (i + 1) / (want + 1)) for i in range(want)))
