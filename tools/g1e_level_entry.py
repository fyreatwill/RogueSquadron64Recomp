#!/usr/bin/env python3
"""s6932: what precedes each upward latency level step on a locked display. Per ring, walks 1-frame latency (same basis as g1e_present_latency.py),
finds sustained level rises (median of the next 30 presents at least one vsync above the previous 30), and prints the largest Q gap, tp_ms, acq_ms and gpu_ms in the
1.6 s around the step (-1 s to +0.6 s: the detector fires up to 30 presents early, so a window ending at the trigger misses the step itself, s6932), against the same statistics over the whole ring. Control: rings with the ROGUESQ_PRESENT_TEST_STALL lever must show their ~200 ms gap at the step.
usage: g1e_level_entry.py [--hz 60] ring..."""
import argparse, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--hz',type=float,default=60); a=ap.parse_args()
v=1e3/a.hz; W=30
for f in a.files:
    Q=[];P={}
    for l in open(f,errors='replace'):
        p=l.split()
        if p[:1]==['Q'] and len(p)>=13 and l.endswith('\n'):
            d=dict(x.split('=') for x in p[2:]); d['t']=float(p[1]); Q.append(d)
        elif p[:1]==['P'] and len(p)>=4: P[int(p[2][4:])]=float(p[3][3:])
    R=[]
    for q in Q:
        k=int(q['mtl'])
        if q['skip']=='0' and P.get(k,0)>0: R.append((q['t'],(P[k]-q['t'])*1e3+float(q['tp_ms']),float(q['tp_ms']),float(q['acq_ms']),float(q['gpu_ms'])))
    if len(R)<4*W: print(f.split('/')[-1],'too few rows'); continue
    gaps=[(R[i][0]-R[i-1][0])*1e3 for i in range(1,len(R))]
    print('%s rows=%d t=%.0fs gap p50/p99/max %.1f/%.1f/%.1f'%(f.split('/')[-1],len(R),R[-1][0]-R[0][0],st.median(gaps),sorted(gaps)[int(.99*len(gaps))],max(gaps)))
    i=W; last=-1e9
    while i<len(R)-W:
        b=st.median(x[1] for x in R[i-W:i]); c=st.median(x[1] for x in R[i:i+W])
        if c-b>=0.75*v and R[i][0]-last>2:
            last=R[i][0]; w=[j for j in range(1,len(R)) if R[i][0]-1<=R[j][0]<=R[i][0]+.6]
            g=max(((R[j][0]-R[j-1][0])*1e3,j) for j in w)
            print('  +%.0fs %.0f->%.0f ms maxgap %.1f ms at -%.0f ms, 1s max tp %.1f acq %.1f gpu %.1f'%(R[i][0]-R[0][0],b,c,g[0],(R[i][0]-R[g[1]][0])*1e3,max(R[j][2] for j in w),max(R[j][3] for j in w),max(R[j][4] for j in w)))
            i+=W
        i+=1
