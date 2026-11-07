#!/usr/bin/env python3
"""s6932: per-arm table for the owner-recipe present rings. Last N seconds of each ring, ungated reading of acq_ms.
Columns: presents/s (Q rows), distinct game frames/s (distinct fb-gen pairs), on-screen rows, lat p50/p99 (same basis as g1e_present_latency.py: P at minus Q time plus tp_ms, so a nextDrawable wait counts),
acq p50 and share over 5 ms, and the 1 s median latency range. usage: g1e_owner_hz_score.py [--last 120] ring...
Control: a ring whose Q and P rows join gives on>0; a ring without reports prints on=0 and must not be read as low latency."""
import re, sys, argparse, os, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--last',type=float,default=120); a=ap.parse_args()
pc=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else 0
print('arm | Q/s | gen/s | on | lat p50/p99 | 1s med min..max | acq p50 | acq>5 %')
for f in a.files:
    Q={}; P=[]
    for l in open(f,errors='replace'):
        p=l.split()
        if len(p)<3: continue
        kv=dict(x.split('=',1) for x in p[2:] if '=' in x)
        if p[0]=='Q': Q.setdefault(int(kv['mtl']),(float(p[1]),float(kv.get('acq_ms',0)),kv.get('gen'),float(kv.get('tp_ms',0)))) if kv.get('skip')=='0' else None
        elif p[0]=='P' and float(kv.get('at',0))>0: P.append((int(kv['mtl']),float(kv['at'])))
    if not Q: print(os.path.basename(f),'| empty'); continue
    end=max(q[0] for q in Q.values()); t0=end-a.last
    qs=[q for q in Q.values() if q[0]>=t0]
    lat=[((at-Q[i][0])*1000+Q[i][3],int(Q[i][0])) for i,at in P if i in Q and Q[i][0]>=t0]
    sec={}
    for v,s in lat: sec.setdefault(s,[]).append(v)
    med=[st.median(v) for v in sec.values()]
    acq=[q[1] for q in qs]
    print('%s | %.1f | %.1f | %d | %.1f/%.1f | %.1f..%.1f | %.2f | %.1f'%(os.path.basename(f)[5:-4],len(qs)/a.last,len({q[2] for q in qs})/a.last,len(lat),
      pc([v for v,_ in lat],.5),pc([v for v,_ in lat],.99),min(med or [0]),max(med or [0]),pc(acq,.5),100*sum(x>5 for x in acq)/max(1,len(acq))))
