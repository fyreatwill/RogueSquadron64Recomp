#!/usr/bin/env python3
"""s6885 G1e: does the game's frame rate reach the screen? Reads ROGUESQ_PRESENT_RING files (Q = one row per queued present, P = CoreAnimation's
presented callback). A queued present is a NEW frame if its VI origin differs from the previous queued one; a SHOWN new frame is a present that ran (skip=0), whose origin
differs from the previous present that ran, and whose drawable has presentedTime > 0. Dropped by the compositor = at=0. usage: g1e_present_ring.py <file> ... [--last S]
Window: the last S seconds of the run (flight; early boot is ignored)."""
import re,sys,argparse
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--last',type=float,default=60)
a=ap.parse_args()
def pc(v,p): return sorted(v)[int(p*(len(v)-1))] if v else 0
print('file | secs | queued/s | new/s | skip/s | lost new/s | ran/s | on-screen/s | ca-dropped/s | shown-new/s min/p10/p50 | gap ms p50/p99/max | >25ms gaps/s | latency ms p50/p99 | wl p50/p99 | tp p50/p99 | acq p99 | gpu p50/p99')
for fn in a.files:
    Q=[];P={}
    for l in open(fn,errors='replace'):
        if l[:2]=='Q ':
            p=l.split()
            if len(p)<13 or not l.endswith('\n'): continue  # SIGKILL truncates the last row
            d=dict(x.split('=') for x in p[2:]); d['t']=float(p[1]); Q.append(d)
        elif l[:2]=='P ':
            m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)',l)
            if m: P[int(m[2])]=float(m[3])
    if not Q: print(fn,'no rows'); continue
    t1=Q[-1]['t']; t0=t1-a.last; prev=None; rows=[]
    for q in Q:
        q['new']=prev is not None and q['vi']!=prev; prev=q['vi']
        if q['t']>=t0: rows.append(q)
    secs=rows[-1]['t']-rows[0]['t']; n=lambda f:sum(1 for q in rows if f(q))/secs
    ran=[q for q in rows if q['skip']=='0']
    # a present that ran shows a new frame if its origin differs from the previous present that RAN (skip=1 rows show nothing). Lost = origin
    # changes in the queue that no ran present showed. With 2 queued per frame the skipped copy is not a loss, the ran copy shows that frame.
    pr=None
    for q in ran:
        q['rnew']=pr is not None and q['vi']!=pr; pr=q['vi']
    lost=sum(1 for q in rows if q['new'])-sum(1 for q in ran if q['rnew'])
    at=[]; sn=[]; lat=[]; dropped=0; seen=set()
    for q in ran:
        k=int(q['mtl'])
        if k in seen: continue
        seen.add(k)
        if k not in P: continue
        if P[k]>0:
            at.append(P[k]); lat.append((P[k]-q['t'])*1e3)
            if q['rnew']: sn.append(P[k])
        else: dropped+=1
    gaps=[(y-x)*1e3 for x,y in zip(sorted(at),sorted(at)[1:])]
    per={}
    for x in sn: per[int(x)]=per.get(int(x),0)+1
    v=sorted(per.values())[1:-1] or [0]
    f=lambda k,p:pc([float(q[k]) for q in ran],p)
    print(f"{fn.split('/')[-1]} | {secs:.0f} | {len(rows)/secs:.1f} | {n(lambda q:q['new']):.1f} | {n(lambda q:q['skip']=='1'):.1f} | {lost/secs:.2f} | {len(ran)/secs:.1f} | {len(at)/secs:.1f} | {dropped/secs:.2f} | {v[0]}/{pc(v,.1)}/{pc(v,.5)} | {pc(gaps,.5):.1f}/{pc(gaps,.99):.1f}/{max(gaps or [0]):.1f} | {sum(1 for g in gaps if g>25)/secs:.2f} | {pc(lat,.5):.1f}/{pc(lat,.99):.1f} | {f('wl_ms',.5):.2f}/{f('wl_ms',.99):.2f} | {f('tp_ms',.5):.2f}/{f('tp_ms',.99):.2f} | {f('acq_ms',.99):.2f} | {f('gpu_ms',.5):.2f}/{f('gpu_ms',.99):.2f}")
