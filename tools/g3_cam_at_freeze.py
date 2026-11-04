#!/usr/bin/env python3
"""s6875 G3: camera block at each POSE_FREEZE, per arm. Needs ROGUESQ_G3C_CAMLOG=1 in the arm. Prints the last [camlog] row before
each [posefreeze] (the camera of the frame on screen during the freeze): the 22 floats at *(0x80138D1C)+0x28, pos = words 9..11, and
pos minus the player pos on the freeze row. Then every word's largest difference against the first arm.
Usage: g3_cam_at_freeze.py TAG [TAG ...]   (TAG = scratch/agent/m6/g1_lvl1<TAG>/run.log)"""
import re, sys

def load(tag):
    last, out = None, []
    for ln in open('scratch/agent/m6/g1_lvl1%s/run.log' % tag, 'rb'):
        if ln.startswith(b'[camlog]'):
            m = re.search(rb'n=(\d+) ptr=(\w+) cam=([^ ]*) tt', ln)
            if m:
                last = (int(m.group(1)), m.group(2).decode(), [float(v) for v in m.group(3).split(b',') if v])
        elif ln.startswith(b'[posefreeze]'):
            m = re.search(rb'k=(\d+) vi=(\d+) pos=([^ ]+)', ln)
            out.append((int(m.group(1)), [float(v) for v in m.group(3).split(b',')], last))
    return out

arms = {t: load(t) for t in sys.argv[1:]}
base = sys.argv[1]
for t, rows in arms.items():
    for k, pos, c in rows:
        if not c or len(c[2]) < 12:
            print(t, k, 'no camera row'); continue
        cp = c[2][9:12]
        print('%-12s k=%d n=%d ptr=%s player %s cam %s rel %s' % (t, k, c[0], c[1], ' '.join('%.3f' % v for v in pos),
              ' '.join('%.3f' % v for v in cp), ' '.join('%+.3f' % (a - b) for a, b in zip(cp, pos))))
for t, rows in arms.items():
    if t == base:
        continue
    for (k, _, c), (_, _, b) in zip(rows, arms[base]):
        if c and b and len(c[2]) == len(b[2]):
            d = [abs(x - y) for x, y in zip(c[2], b[2])]
            print('%-12s k=%d vs %s maxdiff %.4f at word %d; rot words 0-8 max %.5f' % (t, k, base, max(d), d.index(max(d)), max(d[:9])))
