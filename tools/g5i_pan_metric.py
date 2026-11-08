#!/usr/bin/env python3
"""s6995 G5i: per scroll from a ROGUESQ_G5G_CAM log, the off-axis angle of the destination craft AFTER the turn (tau >= TURN s) to scroll end:
max and mean. Failure signature (s6907 fixed clock): the view released mid pan, craft back out 20-60 deg. usage: g5i_pan_metric.py LOG [turn=1.6]"""
import sys, math
T=float(sys.argv[2]) if len(sys.argv)>2 else 1.6
S={}
for l in open(sys.argv[1]):
    if l.startswith('#'): continue
    f=l.split(); S.setdefault(int(f[1]),[]).append(f)
for k,v in sorted(S.items()):
    t0=float(v[0][0]); offs=[]
    for f in v:
        r=list(map(float,f[:17])); tau=float(f[21]) if len(f)>21 else r[0]-t0
        E=r[4:7]; B=r[7:10]; o=r[13:16]; g=[B[i]-E[i] for i in range(3)]; gl=math.sqrt(sum(x*x for x in g))
        off=math.degrees(math.acos(max(-1,min(1,sum(o[i]*g[i] for i in range(3))/gl))))
        if tau>=T: offs.append(off)
    mx=max(offs) if offs else -1; mn=sum(offs)/len(offs) if offs else -1
    print(f'scroll {k} t {t0:.1f} dest {v[0][3]} dur {float(v[-1][0])-t0:.2f} post-turn off max {mx:.1f} mean {mn:.1f}')
