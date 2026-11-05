#!/usr/bin/env python3
"""s6885 G1e: shown-frame ORDER from ROGUESQ_PRESENT_RING rows, using W rows (workload -> buffers it really drew).
For each present that ran, the frame shown = newest workload that drew its fb and was submitted before the present composited (Q time - tp_ms + acq_ms).
Step between ran presents: 1 in order, 0 held, >=2 frames missed, <0 BACKWARD. A workload that draws no scanout buffer is not a frame.
The frame identity is by buffer and time, not pixels. usage: g1e_present_order.py <file> ... [--last S]"""
import argparse,bisect,collections
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--last',type=float,default=70); a=ap.parse_args()
print('file | wl/s | frames/s | Q per wl | fb!=vi/s | fwd1/s | held/s | miss2+/s | BACK/s | distinct shown/s | never shown/s | wl-vs-time disagree/s')
for fn in a.files:
    Q=[];W=[]
    for l in open(fn,errors='replace'):
        if not l.endswith('\n'): continue
        p=l.split()
        if l[:2]=='Q ' and len(p)>=13:
            d=dict(x.split('=',1) for x in p[2:]); d['t']=float(p[1]); Q.append(d)
        elif l[:2]=='W ' and len(p)>=4:
            W.append((float(p[1]),int(p[2][3:]),p[3][4:].split(',')))
    if not W: print(fn,'no W rows'); continue
    t1=Q[-1]['t']; t0=t1-a.last
    scan={q['fb'] for q in Q if q['skip']=='0' and q['fb']!='000000' and q['t']>=t0}
    by=collections.defaultdict(list)  # fb -> [(t,wl)]
    frames=[]
    for t,wl,fbs in W:
        for f in fbs:
            if f in scan: by[f].append((t,wl))
        if t>=t0 and any(f in scan for f in fbs): frames.append(wl)
    st=collections.Counter(); prev=None; shown=set(); dis=0; fbne=0; nq=0; wls=set()
    for q in Q:
        if q['t']<t0: continue
        nq+=1; wls.add(int(q['wl']))
        if q['skip']!='0' or q['fb']=='000000': continue
        fbne+=q['fb']!=q['vi']
        comp=q['t']-float(q['tp_ms'])*1e-3+float(q['acq_ms'])*1e-3
        L=by.get(q['fb'],[])
        i=bisect.bisect_right(L,(comp,1<<62))-1
        if i<0: continue
        f=L[i][1]
        j=bisect.bisect_right([x[1] for x in L[max(0,i-8):i+8]],int(q['wl']))-1
        fw=L[max(0,i-8):i+8][j][1] if j>=0 else None
        dis+= fw!=f
        shown.add(f)
        if prev is not None: st[max(min(f-prev,3),-3)]+=1
        prev=f
    S=a.last; fs=set(frames)
    print(f"{fn.split('/')[-1]} | {len(wls)/S:.1f} | {len(fs)/S:.1f} | {nq/max(len(wls),1):.2f} | {fbne/S:.1f} | {st[1]/S:.1f} | {st[0]/S:.2f} | {(st[2]+st[3])/S:.2f} | {sum(st[k] for k in (-1,-2,-3))/S:.2f} | {len(shown&fs)/S:.1f} | {len(fs-shown)/S:.2f} | {dis/S:.2f}")
