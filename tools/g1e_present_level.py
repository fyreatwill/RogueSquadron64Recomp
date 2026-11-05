#!/usr/bin/env python3
"""s6888 G1e: what moves the present latency level. Reads ROGUESQ_PRESENT_RING files. Series = latency per on-screen present (g1e_present_latency.py measure), 1 s medians
quantised to --tol ms; a change = two neighbouring plateaus (>= --hold s each) that differ. Per change: time, from -> to, and inside +-1 s the longest gap between present stamps,
longest gap between on-screen times, max acq_ms (nextDrawable wait), max tp_ms, at=0 reports. Control: every present gap >= --gap ms in the run, and how many had a level change
within +-1.5 s, so a stall that moves nothing counts against H-phase.
usage: g1e_present_level.py ring.txt .. [--from S] [--tol 5] [--hold 3] [--gap 40]"""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--from',dest='t_from',type=float,default=0)
ap.add_argument('--tol',type=float,default=5); ap.add_argument('--hold',type=int,default=3); ap.add_argument('--gap',type=float,default=40)
a=ap.parse_args()
def med(v): v=sorted(v); return v[len(v)//2]
for fn in a.files:
    Q=[];P={}
    for l in open(fn,errors='replace'):
        if l[:2]=='Q ' and l.endswith('\n'):
            p=l.split()
            if len(p)<13: continue
            d=dict(x.split('=') for x in p[2:]); d['t']=float(p[1]); Q.append(d)
        elif l[:2]=='P ':
            m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)',l)
            if m: P[int(m[2])]=float(m[3])
    Q=[q for q in Q if q['skip']=='0']
    if not Q: continue
    t0=Q[0]['t']; R=[]
    for q in Q:
        k=int(q['mtl']); at=P.get(k,-1); t=q['t']-t0
        R.append((t,(at-q['t'])*1e3+float(q['tp_ms']) if at>0 else None,float(q['acq_ms']),float(q['tp_ms']),at))
    R=[r for r in R if r[0]>=a.t_from]
    sec={}
    for r in R:
        if r[1] is not None: sec.setdefault(int(r[0]),[]).append(r[1])
    ks=sorted(sec); m={k:med(sec[k]) for k in ks if len(sec[k])>=20}
    # plateaus: runs of seconds whose medians stay within tol of the run start
    pl=[]
    for k in sorted(m):
        if pl and abs(m[k]-pl[-1][2])<=a.tol and k-pl[-1][1]<=3: pl[-1][1]=k
        else: pl.append([k,k,m[k]])
    pl=[p for p in pl if p[1]-p[0]+1>=a.hold]
    ch=[(y[0],x[2],y[2],x[1]) for x,y in zip(pl,pl[1:]) if abs(x[2]-y[2])>a.tol]
    print(f"{fn.split('/')[-2]}/{fn.split('/')[-1]} presents {len(R)} plateaus "+' '.join(f"{p[0]}-{p[1]}:{p[2]:.0f}" for p in pl))
    gaps=[(y[0],(y[0]-x[0])*1e3) for x,y in zip(R,R[1:])]
    for k,f,t,e in ch:
        w=[r for r in R if e-1<=r[0]<=k+1]; gp=[g for tt,g in gaps if e-1<=tt<=k+1]
        on=sorted(r[4] for r in w if r[4]>0); og=max([(y-x)*1e3 for x,y in zip(on,on[1:])] or [0])
        print(f"  t={e}..{k} {f:.0f}->{t:.0f} | present gap {max(gp or [0]):.0f} on-screen gap {og:.0f} acq {max(r[2] for r in w):.1f} tp {max(r[3] for r in w):.1f} at0 {sum(1 for r in w if r[4]==0)}")
    big=[(t,g) for t,g in gaps if g>=a.gap]; near=sum(1 for t,g in big if any(e-1.5<=t<=k+1.5 for k,f,to,e in ch))
    print(f"  gaps>={a.gap:.0f}ms: {len(big)}, near a change: {near}; max gap away from changes {max([g for t,g in big if not any(e-1.5<=t<=k+1.5 for k,f,to,e in ch)] or [0]):.0f} ms")
    # stall dose table: S rows from ROGUESQ_PRESENT_TEST_STALL. pre = median latency in the 2 s before, post = median 1..3 s after; presents lost = skip rows inside the stall + 50 ms
    S=[]
    for l in open(fn,errors='replace'):
        m=re.match(r'S (\S+) ms=(\d+) slept=(\S+)',l)
        if m: S.append((float(m[1])-t0,int(m[2]),float(m[3])))
    if S:
        def lvl(f,e):
            v=[r[1] for r in R if f<=r[0]<e and r[1] is not None]
            return med(v) if len(v)>=20 else None
        print('  t | dose ms | slept | pre | post | delta ms | delta vsyncs')
        by={}
        for t,ms,sl in S:
            a0=lvl(t-2.2,t-.2); b0=lvl(t+1,t+3)
            if a0 is None or b0 is None: print(f"  {t:.0f} | {ms} | {sl:.1f} | no level"); continue
            by.setdefault(ms,[]).append(b0-a0)
            print(f"  {t:.0f} | {ms} | {sl:.1f} | {a0:.0f} | {b0:.0f} | {b0-a0:+.0f} | {(b0-a0)/16.67:+.1f}")
        print('  dose: deltas '+' ; '.join(f"{k}: "+' '.join(f"{x:+.0f}" for x in v) for k,v in sorted(by.items())))
    # upward steps: on-screen slips (gap >= 30 ms between neighbouring on-screen times) and the level either side, whole flight, stalls excluded
    on=[(r[0],r[4],r[1]) for r in R if r[4]>0 and r[1] is not None]
    up=dn=same=0; sat=0
    for (ta,xa,la),(tb,xb,lb) in zip(on,on[1:]):
        if (xb-xa)*1e3<30 or any(t-.1<=tb<=t+ms/1e3+.3 for t,ms,_ in S): continue
        w0=[x[2] for x in on if tb-1<=x[0]<tb-.05]; w1=[x[2] for x in on if tb+.05<=x[0]<tb+1]
        if len(w0)<20 or len(w1)<20: continue
        d=med(w1)-med(w0)
        if med(w0)>=68: sat+=1
        if d>a.tol: up+=1
        elif d<-a.tol: dn+=1
        else: same+=1
    print(f"  on-screen slips >=30 ms: level up {up} down {dn} same {same} (from level >=68 ms: {sat})")
