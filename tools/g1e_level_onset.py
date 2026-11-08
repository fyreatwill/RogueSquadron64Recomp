#!/usr/bin/env python3
"""s6966: what precedes the onset of a 21:9 drawable-queue level (a run of presents with acquireTexture wait > THR ms).
Reads a present ring (Q/P/W/T/D rows, ROGUESQ_G1E_AQ=2). Onset = first Q of a run of >= --minrun consecutive acq>THR shown presents,
preceded by >= 10 acq<=THR presents. Controls: (c1) short runs (length 1..3, same pre-condition: blips that do not grow) and
(c2) baseline Q rows (acq<=THR, previous 10 and next 3 also <=THR). For the K presents before each row it reports:
  dq    Q->Q interval (game/queue side cadence; a hitch = one long interval, a burst = one short one)
  dw    W->W interval (workload submit cadence, game side)
  dp    P->P presented-time interval (display side)
  tp,wl,gpu  per-Q host ms, and acq of the preceding presents (slope = smooth vsync-phase drift).
Hypotheses: H-hitch (max dq/dw before onset >> baseline), H-burst (min dq << 16.7 before onset), H-vsync-phase (acq ramps up over
the preceding presents with even dq). usage: g1e_level_onset.py ring [--thr 5] [--minrun 8] [--k 3] [--from 0]"""
import sys, argparse, statistics as st, bisect
ap=argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--thr',type=float,default=5); ap.add_argument('--minrun',type=int,default=8)
ap.add_argument("--k",type=int,default=3); ap.add_argument("--pre",type=int,default=10); ap.add_argument('--from',dest='frm',type=float,default=0)
a=ap.parse_args()
Q=[];P={};W=[];T=[]
for l in open(a.ring,errors='replace'):
    p=l.split()
    if len(p)<2 or not l.endswith('\n'): continue
    kv=dict(x.split('=',1) for x in p[2:] if '=' in x)
    try:
        t=float(p[1])
        if p[0]=='Q' and kv.get('skip')=='0' and 'acq_ms' in kv:
            Q.append(dict(t=t,acq=float(kv['acq_ms']),tp=float(kv['tp_ms']),wl=float(kv['wl_ms']),gpu=float(kv['gpu_ms']),m=int(kv['mtl'])))
        elif p[0]=='P' and float(kv.get('at',0))>0: P[int(kv['mtl'])]=float(kv['at'])
        elif p[0]=='W': W.append(t)
        elif p[0]=='T': T.append((t,int(kv['on'])))
    except (KeyError,ValueError): pass
if not Q: sys.exit('no Q rows with acq_ms (G1E_AQ=2 not armed: control failed)')
Q.sort(key=lambda q:q['t']); t0=T[0][0] if T else Q[0]['t']
Q=[q for q in Q if q['t']-t0>=a.frm]
hi=[q['acq']>a.thr for q in Q]; n=len(Q)
def blk_on(t):
    i=bisect.bisect_right([x[0] for x in T],t)-1
    return T[i][1] if i>=0 else -1
def runlen(i):
    j=i
    while j<n and hi[j]: j+=1
    return j-i
pre_ok=lambda i: i>=a.pre+a.k and not any(hi[i-a.pre:i])
onset=[];c1=[];c2=[]
for i in range(n):
    if hi[i] and pre_ok(i):
        r=runlen(i)
        if r>=a.minrun: onset.append(i)
        elif r<=3: c1.append(i)
    elif not hi[i] and pre_ok(i) and i+3<n and not any(hi[i:i+4]) and i%7==0: c2.append(i)
Wt=sorted(W)
def feat(i):
    k=a.k; qs=Q[i-k:i+1]
    dq=[(qs[j+1]['t']-qs[j]['t'])*1e3 for j in range(k)]
    w1=bisect.bisect_right(Wt,Q[i]['t']); ws=Wt[max(0,w1-k-1):w1]
    dw=[(ws[j+1]-ws[j])*1e3 for j in range(len(ws)-1)]
    ps=[P[q['m']] for q in qs if q['m'] in P]
    dp=[(ps[j+1]-ps[j])*1e3 for j in range(len(ps)-1)]
    pa=[q['acq'] for q in Q[i-k:i]]
    return dict(dqmax=max(dq),dqmin=min(dq),dwmax=max(dw) if dw else float('nan'),dwmin=min(dw) if dw else float('nan'),
                dpmax=max(dp) if dp else float('nan'),dpmin=min(dp) if dp else float('nan'),
                tp=max(q['tp'] for q in qs[:-1]),wl=max(q['wl'] for q in qs[:-1]),gpu=max(q['gpu'] for q in qs[:-1]),
                acqpre=pa[-1],acqslope=(pa[-1]-pa[0])/(k-1) if k>1 else 0.0,acq0=Q[i]['acq'])
keys=['dqmax','dqmin','dwmax','dwmin','dpmax','dpmin','tp','wl','gpu','acqpre','acqslope','acq0']
def med(v):
    v=[x for x in v if x==x]; return (st.median(v),sorted(v)[int(.9*(len(v)-1))]) if v else (float('nan'),)*2
F={nm:[feat(i) for i in L] for nm,L in (('onset',onset),('short',c1),('base',c2))}
print('ring %s thr %.1f minrun %d k %d: onsets %d, short blips %d, baseline %d, Q %d'%(a.ring,a.thr,a.minrun,a.k,len(onset),len(c1),len(c2),n))
print('%-9s'%'feature'+''.join('%18s'%nm for nm in F)+'   (median / p90, ms)')
for k in keys:
    print('%-9s'%k+''.join('%18s'%('%.2f / %.2f'%med([f[k] for f in F[nm]])) for nm in F))
print('per onset: t  on  run  dq[-k..0]  dp[-k..0]  acq[-k..0]  tp  wl')
for i in onset:
    print('%7.2f %2d %4d  %s  %s  %s  %.1f %.1f'%(Q[i]['t']-t0,blk_on(Q[i]['t']),runlen(i),
          ','.join('%.1f'%((Q[j+1]['t']-Q[j]['t'])*1e3) for j in range(i-a.k,i)),
          ','.join('%.0f'%((P[Q[j+1]['m']]-P[Q[j]['m']])*1e3) if Q[j]['m'] in P and Q[j+1]['m'] in P else '-' for j in range(i-a.k,i)),
          ','.join('%.1f'%Q[j]['acq'] for j in range(i-a.k,i+1)),max(Q[j]['tp'] for j in range(i-a.k,i)),max(Q[j]['wl'] for j in range(i-a.k,i))))
