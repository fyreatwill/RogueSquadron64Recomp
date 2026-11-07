#!/usr/bin/env python3
"""s6932: same-run score of ROGUESQ_WIDE_LOGQUIET=tog from a present ring. Blocks are 10 s on the ring clock, odd block = quiet. Skips the first --skip s of the ring
(route) and the first 1 s of each block. Prints per parity presents/s, gap p99, gaps over 50 ms per minute, 1-frame latency p50, then the paired neighbour difference
quiet - loud in presents/s with its standard error. usage: g1e_logquiet_blocks.py [--skip 100] ring..."""
import argparse, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--skip',type=float,default=100); a=ap.parse_args()
pc=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else 0
for f in a.files:
    Q=[];P={}
    for l in open(f,errors='replace'):
        p=l.split()
        if p[:1]==['Q'] and len(p)>=13 and l.endswith('\n'):
            d=dict(x.split('=') for x in p[2:])
            if d['skip']=='0': Q.append((float(p[1]),int(d['mtl']),float(d['tp_ms'])))
        elif p[:1]==['P'] and len(p)>=4 and l.endswith('\n'): P[int(p[2][4:])]=float(p[3][3:])
    t0=Q[0][0]+a.skip; B={}
    for i in range(1,len(Q)):
        t=Q[i][0]
        if t<t0 or t%10<1: continue
        lat=(P[Q[i][1]]-t)*1e3+Q[i][2] if P.get(Q[i][1],0)>0 else None
        B.setdefault(int(t//10),[]).append(((t-Q[i-1][0])*1e3,lat))
    ks=sorted(B)[1:-1]
    print(f.split('/')[-1],'blocks',len(ks))
    for par,name in ((0,'loud'),(1,'quiet')):
        g=[x[0] for k in ks if k&1==par for x in B[k]]; L=[x[1] for k in ks if k&1==par for x in B[k] if x[1] is not None]
        sec=9*sum(k&1==par for k in ks)
        print('  %s presents/s %.2f gap p50/p99 %.1f/%.1f gaps>50ms/min %.1f lat p50 %.1f'%(name,len(g)/sec,pc(g,.5),pc(g,.99),sum(x>50 for x in g)*60/sec,pc(L,.5)))
    d=[]
    for k in ks:
        if k&1 and k-1 in B and k+1 in B: d.append(len(B[k])/9-(len(B[k-1])+len(B[k+1]))/18)
    if len(d)>1: print('  paired quiet-loud %.2f +/- %.2f presents/s (n=%d)'%(st.mean(d),st.stdev(d)/len(d)**.5,len(d)))
