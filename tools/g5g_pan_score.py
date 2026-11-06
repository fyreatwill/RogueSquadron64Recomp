#!/usr/bin/env python3
"""s6907 G5g: per scroll, from a ROGUESQ_G5G_CAM log: destination craft off-axis angle over the pan, on/off. usage: g5g_pan_score.py LOG [aspect=1.882] [fovy=45]
Reports peak yaw rate, seconds the craft is on screen in the outer lens (edge zone: stretch 1/cos(off) >= 1.15) and on-screen time."""
import sys, math
R=[list(map(float,l.split())) for l in open(sys.argv[1])]
asp=float(sys.argv[2]) if len(sys.argv)>2 else 1.882; fov=float(sys.argv[3]) if len(sys.argv)>3 else 45
half=math.degrees(math.atan(math.tan(math.radians(fov/2))*asp))
S={}
for r in R: S.setdefault(int(r[1]),[]).append(r)
print(f'half hfov {half:.1f}')
for k,v in sorted(S.items()):
    on=int(v[0][2]); t0=v[0][0]; edge=vis=0; pr=0; prev=None; rows=[]
    for r in v:
        t=r[0]; E=r[4:7]; B=r[7:10]; o=r[13:16]
        g=[B[i]-E[i] for i in range(3)]; gl=math.sqrt(sum(x*x for x in g))
        off=math.degrees(math.acos(max(-1,min(1,sum(o[i]*g[i] for i in range(3))/gl))))
        dt=(t-prev[0]) if prev else 0
        if prev and dt>0:
            a=math.degrees(math.acos(max(-1,min(1,sum(o[i]*prev[1][i] for i in range(3)))))); pr=max(pr,a/dt)
        if off<half:
            vis+=dt
            if 1/math.cos(math.radians(off))>=1.15: edge+=dt
        prev=(t,o); rows.append((t-t0,off))
    fin=rows[-1][1]; samp=' '.join(f'{x[1]:.0f}' for x in rows[::max(1,len(rows)//10)])
    print(f'scroll {k} aim={on} dest {int(v[0][3])} dur {v[-1][0]-t0:.2f} peak turn {pr:.0f} deg/s on-screen {vis:.2f}s edge-zone {edge:.2f}s final off {fin:.1f} off(t): {samp}')
