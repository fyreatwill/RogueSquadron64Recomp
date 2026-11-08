#!/usr/bin/env python3
"""s6950: per-block table for a ROGUESQ_PRESENT_DRAIN_TOGGLE run. Splits the present ring at T rows (written at each drain on/off flip)
and prints, per block: on flag, Q/s, on-screen share, lat p50/p99 (same basis as g1e_owner_hz_score.py), acq p50 and share >5 ms (the
60 Hz level signature, ~15 ms acq), drain drops (D rows), stall doses (from --stall, same t:ms list as ROGUESQ_PRESENT_TEST_STALL,
relative to the first T row). Then on-vs-off summary over blocks with --from <s> or later. usage: g1e_drain_blocks.py ring [--from 95] [--stall LIST]"""
import sys, argparse, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--from',dest='frm',type=float,default=0); ap.add_argument('--stall',default='')
a=ap.parse_args()
pc=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else float('nan')
T=[];Q={};P=[];D=[]
for l in open(a.ring,errors='replace'):
    p=l.split()
    if len(p)<2 or not l.endswith('\n'): continue
    kv=dict(x.split('=',1) for x in p[2:] if '=' in x)
    try:
        if p[0]=='T': T.append((float(p[1]),int(kv['on']),int(kv['blk'])))
        elif p[0]=='D': D.append(float(p[1]))
        elif p[0]=='Q' and len(p)>=13 and kv.get('skip')=='0': Q.setdefault(int(kv['mtl']),(float(p[1]),float(kv['acq_ms']),float(kv['tp_ms'])))
        elif p[0]=='P' and float(kv.get('at',0))>0: P.append((int(kv['mtl']),float(kv['at'])))
    except (KeyError,ValueError): pass
if not T: sys.exit('no T rows: toggle not active (control failed)')
t0=T[0][0]; st_t=[float(x.split(':')[0]) for x in a.stall.split(',') if x]
lat={i:(at-Q[i][0])*1000+Q[i][2] for i,at in P if i in Q}
end=max(q[0] for q in Q.values())
rows=[]
print('blk on | t0..t1 | Q/s | glass | lat p50/p99 | acq p50 | acq>5% | drops | stalls')
for j,(ts,on,k) in enumerate(T):
    te=T[j+1][0] if j+1<len(T) else end
    qs=[(i,q) for i,q in Q.items() if ts<=q[0]<te]
    if not qs or te-ts<5: continue
    L=[lat[i] for i,_ in qs if i in lat]; A=[q[1] for _,q in qs]
    dr=sum(ts<=d<te for d in D); sd=[s for s in st_t if ts-t0<=s<te-t0]
    r=dict(k=k,on=on,ts=ts-t0,te=te-t0,qps=len(qs)/(te-ts),gl=len(L)/len(qs),p50=pc(L,.5),p99=pc(L,.99),a50=pc(A,.5),a5=100*sum(x>5 for x in A)/len(A),dr=dr,sd=sd)
    rows.append(r)
    print('%3d %d | %5.0f..%5.0f | %.1f | %3.0f%% | %.1f/%.1f | %.2f | %4.1f | %d | %s'%(k,on,r['ts'],r['te'],r['qps'],100*r['gl'],r['p50'],r['p99'],r['a50'],r['a5'],dr,','.join('%g'%s for s in sd)))
for on in (1,0):
    R=[r for r in rows if r['on']==on and r['ts']>=a.frm and r['gl']>=.95]
    if R: print('on=%d n=%d lat p50 median %.1f (range %.1f..%.1f), acq>5%% median %.1f, blocks at level (acq>5%% >30) %d'%(on,len(R),st.median(r['p50'] for r in R),min(r['p50'] for r in R),max(r['p50'] for r in R),st.median(r['a5'] for r in R),sum(r['a5']>30 for r in R)))
