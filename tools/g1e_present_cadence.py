#!/usr/bin/env python3
"""s6889 G1e: which display a present ring ran on. Per 30 s bucket: share of on-screen intervals on a 60 Hz grid (16.7 ms multiples, +-1 ms) vs a 144 Hz grid (6.94 ms multiples that are
not also on the 60 Hz grid), median interval, at=0 reports. A latency figure is only comparable between rings on the same grid: s6889 changed displays under a run set.
s6890 --hist: per file, over the last --last seconds of on-screen presents, the interval histogram in vsyncs of the grid the ring sits on, plus the residual of each on-screen time from a
straight 60/s line fitted per 1 s window (p50/p99 of |residual| and peak-to-peak, ms): a steady 60 Hz grid reads ~0, 60 on 144 Hz should read a 13.9/20.8 mix and a few ms.
usage: g1e_present_cadence.py <file> ... [--hist] [--last S]"""
import re,sys
HIST='--hist' in sys.argv
LAST=120.0
if '--last' in sys.argv:
    i=sys.argv.index('--last'); LAST=float(sys.argv[i+1]); del sys.argv[i:i+2]
sys.argv=[x for x in sys.argv if x!='--hist']
def hist(fn,ats):
    ats=sorted(ats)
    if len(ats)<100: print(fn.split('/')[-1],'INVALID: no on-screen presents (at=0 throughout; s6890: window covered). Rates from g1e_present_order.py are not display evidence for this ring.'); return
    ats=[t for t in ats if t>=ats[-1]-LAST]
    iv=[(v-u)*1e3 for u,v in zip(ats,ats[1:])]
    on60=sum(abs(x-16.67*round(x/16.67))<1 and x>8 for x in iv)/len(iv)
    vs=16.667 if on60>.8 else 6.944
    H={}
    for x in iv: k=max(1,round(x/vs)); H[k]=H.get(k,0)+1
    res=[];pp=[]
    w0=ats[0]
    while w0<ats[-1]:
        g=[t for t in ats if w0<=t<w0+1]; w0+=1
        if len(g)<30: continue
        n=len(g); mx=(n-1)/2; my=sum(g)/n
        b=sum((i-mx)*(t-my) for i,t in enumerate(g))/sum((i-mx)**2 for i in range(n))
        r=[(t-(my+b*(i-mx)))*1e3 for i,t in enumerate(g)]
        res+= [abs(x) for x in r]; pp.append(max(r)-min(r))
    top=' '.join(f'{k}v({k*vs:.1f}ms)={H[k]/len(iv)*100:.1f}%' for k in sorted(H) if H[k]/len(iv)>=.002)
    print(f"{fn.split('/')[-1]} n={len(iv)} rate={len(iv)/(ats[-1]-ats[0]):.2f}/s grid={'60' if vs>10 else '144'} {top} | resid p50/p99 {pc(res,.5):.2f}/{pc(res,.99):.2f} ms, p-p/s p50 {pc(pp,.5):.1f}")
def pc(v,p): return sorted(v)[int(p*(len(v)-1))] if v else 0
for fn in sys.argv[1:]:
    A=[]; z={}; first=None
    for l in open(fn,errors='replace'):
        if l[:2]=='P ':
            m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)\s*$',l)
            if not m: continue
            t=float(m[1]); first=first or t; at=float(m[3]); b=int((t-first)//30)
            if at==0: z[b]=z.get(b,0)+1
            else: A.append((b,at))
    A.sort(key=lambda x:x[1]); B={}
    for (b,u),(_,v) in zip(A,A[1:]): B.setdefault(b,[]).append((v-u)*1e3)
    out=[]
    for b,g in sorted(B.items()):
        on60=sum(abs(x-16.67*round(x/16.67))<1 and x>8 for x in g)/len(g)
        on144=sum(abs(x-6.944*round(x/6.944))<.5 and not abs(x-16.67*round(x/16.67))<1 for x in g)/len(g)
        out.append(f'{on60*100:.0f}/{on144*100:.0f}/{pc(g,.5):.1f}/z{z.get(b,0)}')
    print(fn.split('/')[-1],' '.join(out))
    if HIST: hist(fn,[v for _,v in A])
