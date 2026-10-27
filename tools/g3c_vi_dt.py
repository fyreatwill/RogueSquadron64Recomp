#!/usr/bin/env python3
"""Per-VI wall dt distribution from [g3c] lines (skips first quarter). Usage: g3c_vi_dt.py RUNLOG..."""
import re,sys,statistics as st
for p in sys.argv[1:]:
    rows=[(int(m[1]),float(m[2])) for ln in open(p,errors='replace') for m in [re.match(r'\[g3c\] vi=(\d+) t=([\d.]+)',ln)] if m]
    rows=rows[len(rows)//4:]  # skip warmup
    d=[(b[1]-a[1])*1000 for a,b in zip(rows,rows[1:]) if b[0]-a[0]==1]
    q=st.quantiles(d,n=20)
    a=[x for x in d if x<40]
    alt=sum(1 for x,y in zip(a,a[1:]) if (x-16.667)*(y-16.667)<0)/(len(a)-1)
    print(p.split('/')[-2],'n',len(d),'p5 %.1f p25 %.1f p50 %.1f p75 %.1f p95 %.1f'%(q[0],q[4],q[9],q[14],q[18]),'sd<40 %.2f alt %.3f'%(st.pstdev(a),alt),'frac<2ms %.2f'%(sum(x<2 for x in d)/len(d)))
