#!/usr/bin/env python3
"""s6886 G1e: present-to-screen latency over time. Reads ROGUESQ_PRESENT_RING files. Latency = CoreAnimation presentedTime minus the Q stamp of the
present that ran, plus tp_ms: so it starts when the present thread took the finished workload, and a wait in nextDrawable counts. Prints whole-run level occupancy (latency in vsync-sized bins) and the run-length of each level, so a run that sits at one level
(H-depth) reads differently from one that switches (H-bistable). usage: g1e_present_latency.py <file> ... [--last S] [--series] [--hz 60]"""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--last',type=float,default=60)
ap.add_argument('--series',action='store_true'); ap.add_argument('--hz',type=float,default=60)
a=ap.parse_args()
def pc(v,p): return sorted(v)[int(p*(len(v)-1))] if v else 0
print('file | n | lat p50/p99 ms | level occupancy (vsyncs: %) | level changes of 1 s medians | 1 s median min..max')
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
    if not Q: print(fn,'no rows'); continue
    t0=Q[-1]['t']-a.last; S=[]; seen=set()
    for q in Q:
        if q['skip']!='0' or q['t']<t0: continue
        k=int(q['mtl'])
        if k in seen or P.get(k,0)<=0: continue
        seen.add(k); S.append((q['t'],(P[k]-q['t'])*1e3+float(q['tp_ms'])))
    if not S: print(fn,'no presented rows'); continue
    lat=[x for _,x in S]; v=1e3/a.hz; occ={}
    for x in lat: occ[round(x/v)]=occ.get(round(x/v),0)+1
    sec={}
    for t,x in S: sec.setdefault(int(t-S[0][0]),[]).append(x)
    med=[pc(sec[k],.5) for k in sorted(sec)]; lv=[round(x/v) for x in med]
    ch=sum(1 for x,y in zip(lv,lv[1:]) if x!=y)
    print(f"{fn.split('/')[-1]} | {len(S)} | {pc(lat,.5):.1f}/{pc(lat,.99):.1f} | "+' '.join(f"{k}:{100*n/len(lat):.0f}" for k,n in sorted(occ.items()))+f" | {ch} | {min(med):.1f}..{max(med):.1f}")
    if a.series: print('  '+' '.join(f"{x:.0f}" for x in med))
