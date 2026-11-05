#!/usr/bin/env python3
"""s6888 G1e: on-screen slips (neighbouring on-screen times >= 30 ms apart, stalls and at=0 spans excluded) per phase, and level before/after each slip split by whether the level was under the
ceiling (--ceil ms, level = median of 1 s before). usage: g1e_present_slips.py ring.txt [--ceil 68] [name:from:to ..]"""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('phases',nargs='*'); ap.add_argument('--ceil',type=float,default=68); ap.add_argument('--from',dest='f',type=float,default=60)
a=ap.parse_args()
Q=[];P={};S=[]
for l in open(a.ring,errors='replace'):
    if l[:2]=='Q ' and l.endswith('\n'):
        p=l.split()
        if len(p)<13: continue
        d=dict(x.split('=') for x in p[2:])
        if d['skip']=='0': Q.append((float(p[1]),int(d['mtl']),float(d['tp_ms'])))
    elif l[:2]=='P ':
        m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)',l)
        if m: P[int(m[2])]=float(m[3])
    elif l[:2]=='S ':
        m=re.match(r'S (\S+) ms=(\d+)',l)
        if m: S.append((float(m[1]),int(m[2])))
t0=Q[0][0]
def med(v): v=sorted(v); return v[len(v)//2]
R=[(t-t0,P[k],(P[k]-t)*1e3+tp) for t,k,tp in Q if P.get(k,0)>0 and t-t0>=a.f]
sl=[]
for (ta,xa,la),(tb,xb,lb) in zip(R,R[1:]):
    g=(xb-xa)*1e3
    if g<30 or g>200 or any(s-t0-.1<=tb<=s-t0+ms/1e3+.3 for s,ms in S): continue
    w0=[x[2] for x in R if tb-1<=x[0]<tb-.05]; w1=[x[2] for x in R if tb+.05<=x[0]<tb+1]
    sl.append((tb,g,med(w0) if len(w0)>=20 else None,med(w1) if len(w1)>=20 else None))
c={}
for t,g,b,e in sl:
    if b is None or e is None: continue
    k=('under' if b<a.ceil else 'ceiling','up' if e-b>5 else 'down' if e-b<-5 else 'same'); c[k]=c.get(k,0)+1
print(a.ring.split('/')[-1],'slips',len(sl),'|',' '.join(f"{k[0]}-{k[1]}:{v}" for k,v in sorted(c.items())))
for ph in a.phases:
    n,f,e=ph.split(':'); f=float(f); e=float(e); k=sum(1 for s in sl if f<=s[0]<e); print(f"  {n} {f:.0f}-{e:.0f}: slips {k} = {k/(e-f):.3f}/s")
