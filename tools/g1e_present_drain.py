#!/usr/bin/env python3
"""s6889 G1e: score ROGUESQ_PRESENT_DRAIN from ROGUESQ_PRESENT_RING files. Per file, over the last --last seconds: drops (D rows) and drops/s, latency p50/p99
(Q stamp minus tp_ms to CoreAnimation presentedTime, as g1e_present_latency.py), on-screen rate, slips/s (on-screen gap > 25 ms), and per drop the median latency
in the 0.2 s before and 0.1-0.4 s after (a slip raises the level only ~0.3 s before the median trips, so a 1 s window reads the old level), plus whether an
on-screen gap > 25 ms fell within 200 ms after the drop (a drop the viewer sees as a repeat, not an omitted frame). --all also prints every drop over the whole run, by
level drop size. usage: g1e_present_drain.py <file> ... [--last S] [--all]"""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--last',type=float,default=120); ap.add_argument('--all',action='store_true')
a=ap.parse_args()
def pc(v,p): return sorted(v)[int(p*(len(v)-1))] if v else 0.0
print('file | s | drops drops/s | lat p50/p99 | on-screen/s | slips/s | drop: before->after median, repeats within 150 ms')
for fn in a.files:
    Q=[];P={};D=[]
    for l in open(fn,errors='replace'):
        if l[:2]=='Q ' and l.endswith('\n'):
            p=l.split()
            if len(p)<13: continue
            d=dict(x.split('=') for x in p[2:]); d['t']=float(p[1]); Q.append(d)
        elif l[:2]=='P ':
            m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)\s*$',l)
            if m: P[int(m[2])]=float(m[3])
        elif l[:2]=='D ':
            m=re.match(r'D (\S+) med=(\S+)\s*$',l)
            if m: D.append(float(m[1]))
    if not Q: print(fn,'no rows'); continue
    t1=Q[-1]['t']; t0=t1-a.last; L=[]; seen=set()
    for q in Q:
        k=int(q['mtl'])
        if q['skip']!='0' or k in seen or k not in P or P[k]==0: continue
        seen.add(k); L.append((q['t'],(P[k]-q['t'])*1e3+float(q['tp_ms']),P[k]))
    W=[x for x in L if x[0]>=t0]
    on=sorted(x[2] for x in W)
    gaps=[(u,u-v) for u,v in zip(on[1:],on)]
    slips=[u for u,g in gaps if g>0.025]
    Dw=[t for t in D if t>=t0]
    allon=sorted(x[2] for x in L); allg=list(zip(allon,allon[1:]))
    def score(t):
        b=[x[1] for x in L if t-.2<=x[0]<t]; c=[x[1] for x in L if t+.1<=x[0]<t+.4]
        r=any(t<=v<=t+.2 and u-v>0.025 for v,u in allg)
        return (pc(b,.5),pc(c,.5),r) if b and c else None
    S=[x for x in map(score,Dw) if x]
    ba=[(b,c) for b,c,_ in S]; rep=sum(r for *_,r in S)
    if a.all:
        A=[(t-Q[0]['t'],)+x for t in D for x in [score(t)] if x]
        moved=[x for x in A if x[1]-x[2]>=10]; still=[x for x in A if x[1]-x[2]<10]
        print(f"  all {len(A)}: lowered >=10 ms {len(moved)} (repeat {sum(x[3] for x in moved)}), not lowered {len(still)} (repeat {sum(x[3] for x in still)}); not lowered at t=",' '.join(f'{x[0]:.0f}' for x in still[:12]))
    span=(on[-1]-on[0]) if len(on)>1 else 1
    lat=[x[1] for x in W]
    s=' '.join(f'{b:.0f}->{c:.0f}' for b,c in ba[:6])
    print(f"{fn.split('/')[-1]} | {span:.0f} | {len(Dw)} {len(Dw)/span:.2f} | {pc(lat,.5):.1f}/{pc(lat,.99):.1f} | {len(on)/span:.2f} | {len(slips)/span:.3f} | {s} rep {rep}/{len(Dw)}")
