#!/usr/bin/env python3
"""s6933: H-overrun table. Seconds binned by [g1b] sd_wall (mean ms per gfx task that second), mean tasks/s per bin, from the last N s of each log.
A two-VI lock breaking as the task cost crosses 16.7 ms shows as tasks/s climbing from ~30 to 60 across the 15-18 ms bins. usage: g1e_overrun_bins.py [--last 200] log..."""
import re, argparse, collections, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('logs',nargs='+'); ap.add_argument('--last',type=int,default=200); a=ap.parse_args()
G=re.compile(rb'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)')
B=collections.defaultdict(list); n=0
for f in a.logs:
    g={}
    for l in open(f,'rb'):
        m=G.match(l)
        if m: g[int(m[1])]=(int(m[3]),float(m[4]))
    tm=max(g)
    for t,(k,w) in g.items():
        if t>tm-a.last and t<tm and k>=10: B[int(w)].append(k); n+=1
print('seconds',n)
print('sd_wall ms | secs | tasks/s mean | min..max')
for b in sorted(B): print('%2d-%2d | %4d | %5.1f | %d..%d'%(b,b+1,len(B[b]),st.mean(B[b]),min(B[b]),max(B[b])))
