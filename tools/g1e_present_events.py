#!/usr/bin/env python3
"""s6887 G1e: present behaviour per window-event phase. Reads a ROGUESQ_PRESENT_RING file and a list of phases "name:from:to" in seconds on the ring
clock (0 = first Q row, about window open); --align shifts them so that --align-at seconds lands on the first off-screen report after t=30. Per phase: presents/s, reports/s,
reports with presentedTime 0, on-screen/s, latency p50/p99 (g1e_present_latency.py measure), unreported presents, longest gap between on-screen times.
usage: g1e_present_events.py ring.txt --align-at 125 name:a:b ..."""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('phases',nargs='+'); ap.add_argument('--align-at',type=float)
a=ap.parse_args()
def pc(v,p): return sorted(v)[int(p*(len(v)-1))] if v else 0
Q={};P={}
for l in open(a.ring,errors='replace'):
    if l[:2]=='Q ' and l.endswith('\n'):
        p=l.split()
        if len(p)<13: continue
        d=dict(x.split('=') for x in p[2:])
        if d['skip']=='0': Q[int(d['mtl'])]=(float(p[1]),float(d['tp_ms']))
    elif l[:2]=='P ':
        m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)',l)
        if m: P[int(m[2])]=(float(m[1]),float(m[3]))
t0=min(t for t,_ in Q.values()); sh=0
if a.align_at is not None:
    z=[Q[k][0]-t0 for k,(t,at) in P.items() if at==0 and k in Q and Q[k][0]-t0>30]
    if z: sh=min(z)-a.align_at
print(f"{a.ring.split('/')[-1]} presents {len(Q)} reports {len(P)} unreported {len(set(Q)-set(P))} shift {sh:+.1f}s")
print('phase | s | presents/s | reports/s | at0 | on-screen/s | lat p50/p99 ms | unreported | max on-screen gap ms')
for ph in a.phases:
    n,f,e=ph.split(':'); f=float(f)+sh; e=float(e)+sh
    ks=[k for k,(t,_) in Q.items() if f<=t-t0<e]; rep=[k for k in ks if k in P]
    on=[k for k in rep if P[k][1]>0]; lat=[(P[k][1]-Q[k][0])*1e3+Q[k][1] for k in on]
    ts=sorted(P[k][1] for k in on); gap=max([(y-x)*1e3 for x,y in zip(ts,ts[1:])] or [0]); d=e-f
    print(f"{n} | {d:.0f} | {len(ks)/d:.1f} | {len(rep)/d:.1f} | {len(rep)-len(on)} | {len(on)/d:.1f} | {pc(lat,.5):.1f}/{pc(lat,.99):.1f} | {len(ks)-len(rep)} | {gap:.0f}")
