#!/usr/bin/env python3
"""s7008 G5e: offline geometry of the dd>1 64x64 terrain window against the view frustum, from a ROGUESQ_G3E_TRACE file.
Uses site 11 (eye qx,qz floats, cells), site 13 (pre-clamp frustum bounds) per window call; heading = bounds centre - eye
(s6901: dot with the true camera forward >= 0.99). For each call it re-places the window as apply_s6901 does (w=d=min(bounds,64),
centre eye + K*fwd, clamped into the bounds) for several K, casts the centre ray and the two side rays (+-half-FOV) from the eye and
reports, per K and aspect: median forward depth (cells) where the centre ray leaves the box, where the side rays leave it, and the
share of side rays that leave through a SIDE face before the centre ray's depth (= a visible side/corner edge unless fogged there).
usage: g5e_window_geom.py trace [K,...] ; tan(half hfov) taken from the s6837 hangar numbers (vfov 45): 4:3 0.78, 16:9 1.21, 21:9 1.57."""
import sys,struct,math,statistics as S
def s(u): u=int(u); return u-2**32 if u>=2**31 else u
def f(u): return struct.unpack('<f',struct.pack('<I',int(u)))[0]
Ks=[float(k) for k in (sys.argv[2].split(',') if len(sys.argv)>2 else '0,8,16,30'.split(','))]
cur={};calls=[]
for ln in open(sys.argv[1]):
    p=ln.split(); site=int(p[2]); a=p[3:]
    if site==11: cur['e']=(f(a[0]),f(a[1]))
    elif site==13 and 'e' in cur: calls.append((cur['e'],tuple(s(x) for x in a)))
calls=calls[::5]
def place(e,b,K):
    ex,ez=e; px0,px1,pz0,pz1=b; dx=.5*(px0+px1)-ex; dz=.5*(pz0+pz1)-ez; n=math.hypot(dx,dz)
    if n<1e-3: return None
    dx/=n; dz/=n; w=min(px1-px0,64); d=min(pz1-pz0,64)
    a=math.floor(ex+K*dx-.5*w); a=min(a,px1-w); a=max(a,px0); x0,x1=a,a+w
    a=math.floor(ez+K*dz-.5*d); a=min(a,pz1-d); a=max(a,pz0); z0,z1=a,a+d
    return (dx,dz),(x0,x1,z0,z1)
def exit_t(ex,ez,ux,uz,box):
    x0,x1,z0,z1=box; t=1e9; face=None
    for lo,hi,o,u,nm in ((x0,x1,ex,ux,'x'),(z0,z1,ez,uz,'z')):
        if abs(u)<1e-9: continue
        tt=((hi if u>0 else lo)-o)/u
        if tt<t: t,face=tt,nm
    return max(t,0.0),face
for asp,tn in (('16:9',1.21),('21:9',1.57)):
    ha=math.atan(tn)
    for K in Ks:
        cd=[];sd=[];side=0;tot=0
        for e,b in calls:
            r=place(e,b,K)
            if not r: continue
            (fx,fz),box=r; tc,fc=exit_t(e[0],e[1],fx,fz,box); cd.append(tc)
            for sg in (-1,1):
                c,sn=math.cos(sg*ha),math.sin(sg*ha); ux=fx*c-fz*sn; uz=fx*sn+fz*c
                t,fa=exit_t(e[0],e[1],ux,uz,box); dep=t*math.cos(ha); sd.append(dep); tot+=1
                if dep<tc-2: side+=1
        print(f"{asp} K={K:4.0f} calls={len(cd)} centre-exit med={S.median(cd):5.1f} side-exit depth med={S.median(sd):5.1f} p10={sorted(sd)[len(sd)//10]:5.1f} side-before-centre={100*side/max(1,tot):5.1f}%")
