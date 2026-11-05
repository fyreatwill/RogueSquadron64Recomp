#!/usr/bin/env python3
"""s6886 G1e: what moves present latency between levels? For each ROGUESQ_PRESENT_RING file, finds each sustained step of Q-to-screen latency (median of the 30 presents
before vs after differs by >= 10 ms) and prints the present gap, wl_ms, acq_ms, gpu_ms and CA gap at the step. usage: g1e_present_step.py <file> ... [--max N]"""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--max',type=int,default=6)
a=ap.parse_args()
med=lambda v:sorted(v)[len(v)//2]
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
    R=[];seen=set()
    for q in Q:
        k=int(q['mtl'])
        if q['skip']!='0' or k in seen or P.get(k,0)<=0: continue
        seen.add(k); q['lat']=(P[k]-q['t'])*1e3; q['at']=P[k]; R.append(q)
    if len(R)<80: print(fn.split('/')[-1],'too few rows'); continue
    steps=[];i=30
    while i<len(R)-30:
        b=med([r['lat'] for r in R[i-30:i]]); c=med([r['lat'] for r in R[i:i+30]])
        if abs(c-b)>=10:
            j=max(range(i-6,i+6),key=lambda n:abs(R[n]['lat']-R[n-1]['lat']))
            w=R[j-3:j+3]
            steps.append((R[j]['t']-R[0]['t'],b,c,max((y['t']-x['t'])*1e3 for x,y in zip(w,w[1:])),max((y['at']-x['at'])*1e3 for x,y in zip(w,w[1:])),max(float(r['wl_ms']) for r in w),max(float(r['acq_ms']) for r in w),max(float(r['gpu_ms']) for r in w))); i=j+40
        else: i+=1
    up=sum(1 for s in steps if s[2]>s[1])
    print(f"{fn.split('/')[-1]}: {len(R)} presents, {len(steps)} steps, {up} up, {len(steps)-up} down")
    for s in steps[:a.max]: print("  t=%.1f s %.0f->%.0f ms | Q gap %.1f | CA gap %.1f | wl %.1f | acq %.1f | gpu %.1f"%s)
