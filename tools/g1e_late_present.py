#!/usr/bin/env python3
"""s6966: stage times of single-vsync-late presents (P->P 30-40 ms) vs normal (15-18.5 ms) in a present ring: dq Q->Q, wg W gap, wl/tp/acq/gpu ms, q2s Q->screen. usage: g1e_late_present.py ring..."""
import sys,statistics as st,bisect
pc=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else float('nan')
for f in sys.argv[1:]:
    Q={};P=[];W=[]
    for l in open(f,errors='replace'):
        p=l.split()
        if len(p)<3 or not l.endswith('\n'): continue
        kv=dict(x.split('=',1) for x in p[2:] if '=' in x)
        try:
            if p[0]=='Q' and kv.get('skip')=='0' and 'acq_ms' in kv: Q[int(kv['mtl'])]=(float(p[1]),float(kv['wl_ms']),float(kv['tp_ms']),float(kv['acq_ms']),float(kv['gpu_ms']))
            elif p[0]=='P' and float(kv.get('at',0))>0: P.append((float(kv['at']),int(kv['mtl'])))
            elif p[0]=='W': W.append(float(p[1]))
        except (KeyError,ValueError): pass
    P.sort(); W.sort(); Qt=sorted(q[0] for q in Q.values())
    rows={'miss':[],'norm':[]}
    for j in range(1,len(P)):
        d=(P[j][0]-P[j-1][0])*1e3; m=P[j][1]
        if m not in Q or P[j-1][1] not in Q: continue
        q=Q[m]; qp=Q[P[j-1][1]]
        # W gap before this Q
        i=bisect.bisect_right(W,q[0]); wg=(W[i-1]-W[i-2])*1e3 if i>=2 else float('nan')
        r=dict(dq=(q[0]-qp[0])*1e3,wl=q[1],tp=q[2],acq=q[3],gpu=q[4],q2s=(P[j][0]-q[0])*1e3,wg=wg)
        if d>=30 and d<40: rows['miss'].append(r)
        elif 15<d<18.5: rows['norm'].append(r)
    print(f, 'single-vsync misses',len(rows['miss']),'normal',len(rows['norm']))
    for k in ['dq','wg','wl','tp','acq','gpu','q2s']:
        print('  %-4s miss p10/p50/p90 %6.1f %6.1f %6.1f | normal %6.1f %6.1f %6.1f'%(k,*(pc([r[k] for r in rows['miss']],x) for x in (.1,.5,.9)),*(pc([r[k] for r in rows['norm']],x) for x in (.1,.5,.9))))
    late=sum(r['dq']>25 for r in rows['miss']); wlate=sum(r['wg']>25 for r in rows['miss'])
    print('  misses whose Q came >25 ms after previous Q: %d/%d; whose W gap >25 ms: %d'%(late,len(rows['miss']),wlate))
