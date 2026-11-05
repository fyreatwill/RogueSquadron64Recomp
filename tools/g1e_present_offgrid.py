#!/usr/bin/env python3
"""s6891 G1e: what the off-pattern intervals of 60 fps on a 144 Hz grid are. On-screen intervals in vsyncs (6.944 ms); 2v/3v is the expected 13.9/20.8 mix, 1v and 4v are off pattern.
H-boundary: a present landing one vsync off near a boundary gives a 1v next to a 4v (or 3v+1v pairs that sum to the expected time), so the sum of the pair is 5v and the on-screen line is
not displaced afterwards. H-producer: off-pattern intervals follow jitter in the time the present reached the queue (Q t), so Q-interval deviation at that index is large and pairs are not
adjacent. Prints per file: share of 1v/4v, share of 1v with a 4v neighbour, sum of neighbours, Q-interval deviation (ms) at off-pattern vs on-pattern rows, against a same-file shuffled
expectation of adjacency. usage: g1e_present_offgrid.py <ring> ... [--last S]"""
import re,sys,random,statistics as st
LAST=120.0
if '--last' in sys.argv:
    i=sys.argv.index('--last'); LAST=float(sys.argv[i+1]); del sys.argv[i:i+2]
V=1e3/144
for fn in sys.argv[1:]:
    P=[]
    for l in open(fn,errors='replace'):
        m=re.match(r'P (\S+) mtl=(\d+) at=(\S+)\n',l)
        if m: P.append((int(m[2]),float(m[1]),float(m[3])))
    Qt={}
    for l in open(fn,errors='replace'):
        if l[:2]=='Q ':
            m=re.search(r'^Q (\S+) .* mtl=(\d+)',l)
            if m: Qt[int(m[2])]=float(m[1])
    S=[x for x in P if x[2]>0]
    if len(S)<100: print(fn.split('/')[-1],'INVALID: no on-screen presents'); continue
    S.sort(key=lambda x:x[2]); S=[x for x in S if x[2]>=S[-1][2]-LAST]
    iv=[(b[2]-a[2])*1e3 for a,b in zip(S,S[1:])]
    k=[max(1,round(x/V)) for x in iv]; n=len(k)
    off=[i for i,x in enumerate(k) if x in(1,4)]
    ones=[i for i in off if k[i]==1]
    def adj(seq):
        return sum(any(0<=j<n and seq[j]>=4 for j in (i-1,i+1)) for i,x in enumerate(seq) if x==1)
    a=adj(k); r=[]
    for _ in range(50):
        s=k[:]; random.shuffle(s); r.append(adj(s))
    sums={}
    for i in ones:
        for j in (i-1,i+1):
            if 0<=j<n and k[j]>=3: sums[k[i]+k[j]]=sums.get(k[i]+k[j],0)+1
    qd=[]
    for i in range(n):
        ta,tb=Qt.get(S[i][0]),Qt.get(S[i+1][0])
        qd.append(None if ta is None or tb is None else abs((tb-ta)*1e3-16.667))
    qo=[qd[i] for i in off if qd[i] is not None]; qn=[qd[i] for i in range(n) if k[i] in(2,3) and qd[i] is not None]
    H={x:k.count(x) for x in sorted(set(k))}
    f=lambda v:'%.2f/%.2f'%(st.median(v),sorted(v)[int(.9*len(v))]) if v else '-'
    print(fn.split('/')[-1],'n',n,'hist',H,'off %.1f%%'%(100*len(off)/n),'| 1v with >=4v neighbour %d of %d (shuffled %.0f)'%(a,len(ones),sum(r)/len(r)),'pair sums',dict(sorted(sums.items())),'| Q dev p50/p90 ms off',f(qo),'on',f(qn))
