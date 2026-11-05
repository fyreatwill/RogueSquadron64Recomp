#!/usr/bin/env python3
"""s6888 G1e: latency time course around each S row of a present ring. Prints, per stall, median latency in 100 ms bins from -0.2 s to --span s after the stall start, the first 8 rows after
the stall (latency, acq_ms, gap to the previous present), and skip rows during the stall. usage: g1e_present_stall_course.py ring.txt [--span 2.0] [--dose 200]"""
import re,argparse
ap=argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--span',type=float,default=2.0); ap.add_argument('--dose',type=int)
a=ap.parse_args()
Q=[];P={};S=[]
for l in open(a.ring,errors='replace'):
    if l[:2]=='Q ' and l.endswith('\n'):
        p=l.split()
        if len(p)<13: continue
        d=dict(x.split('=') for x in p[2:]); d['t']=float(p[1]); Q.append(d)
    elif l[:2]=='P ':
        m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)',l)
        if m: P[int(m[2])]=float(m[3])
    elif l[:2]=='S ':
        m=re.match(r'S (\S+) ms=(\d+) slept=(\S+)',l)
        if m: S.append((float(m[1]),int(m[2]),float(m[3])))
t0=Q[0]['t']
def med(v): v=sorted(v); return v[len(v)//2]
for s,ms,sl in S:
    if a.dose and ms!=a.dose: continue
    rows=[q for q in Q if s-.2<=q['t']<s+a.span]
    b={}; skips=sum(1 for q in rows if q['skip']!='0' and s<=q['t']<s+sl/1e3+.05)
    live=[q for q in rows if q['skip']=='0']
    for q in live:
        at=P.get(int(q['mtl']),0)
        if at>0: b.setdefault(int((q['t']-s+.2)*10),[]).append((at-q['t'])*1e3+float(q['tp_ms']))
    print(f"t={s-t0:.0f} dose {ms} slept {sl:.0f} skips {skips}: "+' '.join(f"{med(b[k]):.0f}" if k in b else '.' for k in range(int((a.span+.2)*10))))
    after=[q for q in live if q['t']>=s][:8]; pv=None; o=[]
    for q in after:
        at=P.get(int(q['mtl']),0); o.append(f"{(at-q['t'])*1e3+float(q['tp_ms']):.0f}/{float(q['acq_ms']):.0f}/{(q['t']-pv)*1e3 if pv else 0:.0f}"); pv=q['t']
    print('    first lat/acq/gap: '+' '.join(o))
