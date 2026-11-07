#!/usr/bin/env python3
"""s6932: does the present backlog follow the game rate? Locked-display rings only. Splits each ring (after --skip s of route) into --win s windows, and per window takes
presents/s, median 1-frame latency at its start and end, so slope = ms of latency gained per s. Prints slope by rate bin. H-rate: a window with present rate at the display rate
has no spare vsync, slope >= 0; below it slope < 0 until the floor. --hz sets the display rate. A ring without on-screen rows prints nothing: it is not low latency.
Latency basis as g1e_present_latency.py: P at minus Q time plus tp_ms. usage: g1e_rate_drain.py [--hz 60] [--win 5] [--skip 100] ring..."""
import argparse, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--hz',type=float,default=60); ap.add_argument('--win',type=float,default=5); ap.add_argument('--skip',type=float,default=100)
a=ap.parse_args()
allb={}
def binof(r):
    s=r-a.hz
    return '>=-0.5' if s>=-.5 else '-0.5..-1.5' if s>=-1.5 else '-1.5..-3' if s>=-3 else '-3..-8' if s>=-8 else '<-8'
ORDER=['>=-0.5','-0.5..-1.5','-1.5..-3','-3..-8','<-8']
for f in a.files:
    Q={};P={}
    for l in open(f,errors='replace'):
        p=l.split()
        if not l.endswith('\n') or len(p)<3: continue
        if p[0]=='Q' and len(p)>=13:
            d=dict(x.split('=',1) for x in p[2:])
            if d['skip']=='0': Q[int(d['mtl'])]=(float(p[1]),float(d['tp_ms']))
        elif p[0]=='P' and len(p)>=4:
            at=float(p[3][3:])
            if at>0: P[int(p[2][4:])]=at
    rows=sorted((Q[i][0],(P[i]-Q[i][0])*1e3+Q[i][1]) for i in P if i in Q)
    if len(rows)<100: print(f.split('/')[-1],'no on-screen rows'); continue
    t0=min(q[0] for q in Q.values())+a.skip; end=rows[-1][0]; W={}
    for t,l in rows:
        if t>=t0: W.setdefault(int((t-t0)//a.win),[]).append((t,l))
    allq=sorted(q[0] for q in Q.values()); B={}
    import bisect
    for k,v in W.items():
        if len(v)<20 or k+1 not in W: continue
        s=t0+k*a.win; n=bisect.bisect_left(allq,s+a.win)-bisect.bisect_left(allq,s); m=max(5,len(v)//5)
        slope=(st.median(x[1] for x in v[-m:])-st.median(x[1] for x in v[:m]))/a.win
        B.setdefault(binof(n/a.win),[]).append(slope); allb.setdefault(binof(n/a.win),[]).append(slope)
    print(f.split('/')[-1][5:-4],' '.join('%s:n=%d,%+.2f'%(b,len(B[b]),st.mean(B[b])) for b in ORDER if b in B))
print('ALL (rate-hz bin: windows, mean slope ms/s, +/- se)')
for b in ORDER:
    if b in allb:
        v=allb[b]; print('  %-11s n=%3d %+.2f +/- %.2f'%(b,len(v),st.mean(v),st.stdev(v)/len(v)**.5 if len(v)>1 else 0))
