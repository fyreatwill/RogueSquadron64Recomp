#!/usr/bin/env python3
"""s6964: split the present-thread time per Q row of a present ring (last N s) into its measured terms.
wl_ms = wait for the frame's GPU workload (game frame render, H-gpu), acq_ms = acquireTexture/nextDrawable wait (H-drawable/H-pace),
gpu_ms = present composite pass + wait, tp_ms = whole threadPresent. Also: Q-to-Q interval, and latency (P at - Q + tp) split by acq bucket.
usage: g1e_present_split.py [--last 100] ring..."""
import sys, argparse, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--last',type=float,default=100); a=ap.parse_args()
pc=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else 0
print('ring | n | wl p50/p90/>16% | acq p50/p90/>5% | gpu p50/p90/>12% | tp p50/p90 | dQ p50/p90/>20% | corr(acq,prev wl) | lat p50 acq<=5 / acq>5')
for f in a.files:
    Q=[];P={}
    for l in open(f,errors='replace'):
        p=l.split()
        if not l.endswith('\n') or len(p)<3: continue
        kv=dict(x.split('=',1) for x in p[2:] if '=' in x)
        try:
            if p[0]=='Q' and len(p)>=13 and kv.get('skip')=='0': Q.append((float(p[1]),float(kv['wl_ms']),float(kv['acq_ms']),float(kv['gpu_ms']),float(kv['tp_ms']),int(kv['mtl'])))
            elif p[0]=='P' and float(kv.get('at',0))>0: P[int(kv['mtl'])]=float(kv['at'])
        except (KeyError,ValueError): pass
    if not Q: print(f,'| empty'); continue
    t0=Q[-1][0]-a.last; Q=[q for q in Q if q[0]>=t0]
    wl=[q[1] for q in Q]; acq=[q[2] for q in Q]; gpu=[q[3] for q in Q]; tp=[q[4] for q in Q]
    dq=[(Q[i][0]-Q[i-1][0])*1e3 for i in range(1,len(Q))]
    try: c=st.correlation(acq[1:],wl[:-1])
    except Exception: c=float('nan')
    lo=[(P[q[5]]-q[0])*1e3+q[4] for q in Q if q[5] in P and q[2]<=5]; hi=[(P[q[5]]-q[0])*1e3+q[4] for q in Q if q[5] in P and q[2]>5]
    sh=lambda v,t:100*sum(x>t for x in v)/len(v)
    print('%s | %d | %.1f/%.1f/%.1f | %.2f/%.2f/%.1f | %.2f/%.2f/%.1f | %.1f/%.1f | %.1f/%.1f/%.1f | %.2f | %.1f (%d) / %.1f (%d)'%(f.split('/')[-2]+'/'+f.split('/')[-1][5:-4],len(Q),
      pc(wl,.5),pc(wl,.9),sh(wl,16),pc(acq,.5),pc(acq,.9),sh(acq,5),pc(gpu,.5),pc(gpu,.9),sh(gpu,12),pc(tp,.5),pc(tp,.9),pc(dq,.5),pc(dq,.9),sh(dq,20),c,
      pc(lo,.5) if lo else 0,len(lo),pc(hi,.5) if hi else 0,len(hi)))
