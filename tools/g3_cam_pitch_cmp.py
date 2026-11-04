#!/usr/bin/env python3
"""s6875 G3: camera rotation difference at matched camera position, ARM vs BASE ([camlog] rows, ROGUESQ_G3C_CAMLOG=1). For sample rows
of BASE, takes the ARM row nearest in x,z and prints position gap, y gap, and the signed pitch gap (word 5, rotation row 1 col 2).
Usage: g3_cam_pitch_cmp.py BASETAG ARMTAG [ARMTAG ...]   (TAG = scratch/agent/m6/g1_lvl<LEVEL><TAG>/run.log, env LEVEL default 1)"""
import math, os, re, sys

def rows(t):
    r = []
    for ln in open('scratch/agent/m6/g1_lvl%s%s/run.log' % (os.environ.get('LEVEL', '1'), t), 'rb'):
        if ln.startswith(b'[camlog]'):
            m = re.search(rb'ptr=80138458 cam=([^ ]*) tt', ln)
            if m:
                r.append([float(v) for v in m.group(1).split(b',') if v])
    return r

a = rows(sys.argv[1])
for t in sys.argv[2:]:
    b = rows(t)
    print(t, 'rows', len(b))
    for i in range(100, min(len(a), 1000), 150):
        p = a[i]
        q = min(b, key=lambda c: (c[9] - p[9]) ** 2 + (c[11] - p[11]) ** 2)
        print('  x %.2f z %.2f dpos %.4f dy %+.4f pitch base %.5f arm %.5f d %+.5f' % (p[9], p[11], math.hypot(q[9] - p[9], q[11] - p[11]),
              q[10] - p[10], p[5], q[5], q[5] - p[5]))
