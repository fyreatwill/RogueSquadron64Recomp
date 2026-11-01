"""s6712: categorise the Gfx Thread factor5_ucode subtree of a `sample` file (interp / bridge / printf / probes / G1E_AQ instrument). (tools/sample_self.py does per-function self time) usage: sample_gfx_split.py <sample.txt>"""
import re,collections,sys
lines=open(sys.argv[1]).read().split('\n')
s=[i for i,l in enumerate(lines) if 'Gfx Thread' in l][0]
rx=re.compile(r'^([\s+!:|]*)(\d+) (.*?)(\s+\(in .*|\s+\[0x.*)?$')
nodes=[]
for l in lines[s+1:]:
    if re.match(r'\s+\d+ Thread_',l): break
    m=rx.match(l)
    if m: nodes.append((len(m.group(1)),int(m.group(2)),re.sub(r'\(.*','',m.group(3).strip())[:60]))
cat=collections.Counter(); pr=collections.Counter(); stack=[]
for i,(d,c,n) in enumerate(nodes):
    while stack and stack[-1][0]>=d: stack.pop()
    kids=[];md=None
    for d2,c2,n2 in nodes[i+1:]:
        if d2<=d: break
        if md is None: md=d2
        if d2==md: kids.append(c2)
    sc=c-sum(kids); stack.append((d,n)); names=[x[1] for x in stack]
    if sc<=0 or 'factor5_ucode' not in names: continue
    if 'rs64_g1e_aq_spin' in names: k='ctl-spin'
    elif 'std::chrono::steady_clock::now' in names and 'rsp_dpc_submit' in names: k='instr-clock'
    elif 'rsp_dpc_submit' in names: k='bridge'
    elif any('printf' in x or 'fwrite' in x or x.startswith('__sfvwrite') or 'fflush' in x for x in names):
        k='printf'; pr[[x for x in names if x.startswith('rs64') or x.startswith('factor5') or 'printf' in x][0:3].__str__()]+=sc
    elif any(x.startswith('getenv') or 'findenv' in x for x in names): k='getenv'; pr['getenv<-'+names[names.index([x for x in names if 'getenv' in x][0])-1]]+=sc
    elif n.startswith('RSP::') or n.startswith('factor5_ucode') or n.startswith('dma_rdram') or n.startswith('_platform_mem'): k='interp'
    elif n.startswith('rs64_') or any(x.startswith('rs64_') for x in names[names.index([x for x in names if x.startswith('factor5_ucode')][0]):]): k='probe:'+next(x for x in names[::-1] if x.startswith('rs64_'))
    else: k='other:'+n
    cat[k]+=sc
tot=sum(cat.values()); print('in factor5_ucode subtree',tot)
for k,c in cat.most_common(28): print(f'{c:6d} {100*c/tot:5.1f}% {k}')
print('--- printf/getenv callers'); 
for k,c in pr.most_common(8): print(c,k)
