#!/usr/bin/env python3
"""s6889 G1e: which display a present ring ran on. Per 30 s bucket: share of on-screen intervals on a 60 Hz grid (16.7 ms multiples, +-1 ms) vs a 144 Hz grid (6.94 ms multiples that are
not also on the 60 Hz grid), median interval, at=0 reports. A latency figure is only comparable between rings on the same grid: s6889 changed displays under a run set.
usage: g1e_present_cadence.py <file> ..."""
import re,sys
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
