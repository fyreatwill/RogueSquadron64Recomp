#!/usr/bin/env python3
"""s6876 G3: match the [camlog] rows of two arms. Counts exact camera-block rows in common (30 Hz repeats share nearly all, so 0 means a real
difference), then samples rotation and position gaps at matched x,z.
Usage: g3_cam_align.py LEVEL TAG_A TAG_B   (TAG = scratch/agent/m6/g1_lvl<LEVEL><TAG>/run.log)"""
import math, re, sys
def rows(p):
    r=[]
    for ln in open(p,'rb'):
        if ln.startswith(b'[camlog]'):
            m=re.search(rb'n=(\d+) ptr=80138458 cam=([^ ]*) tt',ln)
            if m: r.append((int(m.group(1)),[float(v) for v in m.group(2).split(b',') if v],m.group(2)))
        elif ln.startswith(b'[posefreeze]'):
            r.append(('F',ln[:60]))
    return r
lv,A,B=sys.argv[1:4]
a=[x for x in rows(f'scratch/agent/m6/g1_lvl{lv}{A}/run.log') if x[0]!='F']
b=[x for x in rows(f'scratch/agent/m6/g1_lvl{lv}{B}/run.log') if x[0]!='F']
sb={x[2]:x for x in b}
print(A,len(a),B,len(b),'exact-common rows',sum(1 for x in a if x[2] in sb))
first=None;last=None
for x in a:
    if x[2] in sb:
        last=x
        if first is None:first=x
print('first common',first and first[0],'last common',last and last[0], last and last[1][9:12])
# at matched xz, sample
for i in range(0,len(a),max(1,len(a)//10)):
    p=a[i][1]
    q=min(b,key=lambda c:(c[1][9]-p[9])**2+(c[1][11]-p[11])**2)[1]
    print('  n=%d x %.3f y %.3f dpos %.4f dy %+.4f w5 %.5f %.5f d %+.5f maxrot %.5f'%(a[i][0],p[9],p[10],math.hypot(q[9]-p[9],q[11]-p[11]),q[10]-p[10],p[5],q[5],q[5]-p[5],max(abs(u-v) for u,v in zip(p[:9],q[:9]))))
