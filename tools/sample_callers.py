#!/usr/bin/env python3
"""s6934: self samples of leaf symbols by nearest named caller chain, one thread of a `sample` file. usage: sample_callers.py file "Gfx Thread" depth sym [sym...]
With no sym: inclusive samples per symbol, top 40 (recursion counted once per path)."""
import re,sys,collections
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs
f,th,depth=sys.argv[1],sys.argv[2],int(sys.argv[3]); syms=sys.argv[4:]
L=zopen(f,errors='replace').read().split('\n')
s=[i for i,l in enumerate(L) if th in l][0]
rx=re.compile(r'^([\s+!:|]*)(\d+) (.*?)(\s+\(in .*|\s+\[0x.*)?$')
N=[]
for l in L[s+1:]:
    if re.match(r'\s+\d+ Thread_',l): break
    m=rx.match(l)
    if m: N.append((len(m[1]),int(m[2]),re.sub(r'\(.*','',m[3].strip())[:48]))
st=[]; out=collections.Counter(); inc=collections.Counter()
for i,(d,c,n) in enumerate(N):
    while st and st[-1][0]>=d: st.pop()
    k=0; md=None
    for d2,c2,_ in N[i+1:]:
        if d2<=d: break
        if md is None: md=d2
        if d2==md: k+=c2
    if n not in [x[1] for x in st]: inc[n]+=c
    st.append((d,n)); sc=c-k
    if sc>0 and n in syms: out[(n,' < '.join(x[1] for x in st[-2:-2-depth:-1]))]+=sc
if syms:
    for k,v in out.most_common(14): print(v,k[0],'<',k[1])
else:
    for k,v in inc.most_common(44): print(v,k)
