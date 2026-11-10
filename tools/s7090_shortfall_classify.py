"""s7090: classify every pristine retail statement the live tree has fewer copies of (rewritten-same-lhs, control-replaced,
other-stmt-at-addr, addr-block-absent, bare-drop). Usage: python3 tools/s7090_shortfall_classify.py [examples-per-class]"""
import sys, re, collections
sys.path.insert(0,'tools'); import s7090_fixup_statement_census as C
P=C.load_dir('scratch/s7082/regen',{}); L=C.load_dir('../N64Recomp/RecompiledFuncs',{})
pk={v[1][0]:v for v in P.values()}; lk={v[1][0]:(k,v) for k,v in L.items()}
def lhs(st):
    m=re.match(r'^(ctx->[rf]\d+(?:\.\w+)?|MEM_\w+\([^)]*\)|\*?\w+)\s*=',st); return m.group(1) if m else None
kinds=collections.Counter(); ex=collections.defaultdict(list)
for s,(pf,pv) in pk.items():
    if s not in lk: continue
    name,(lf,lv)=lk[s]
    for a,pc in pv[1].items():
        lc=lv[1].get(a,collections.Counter())
        for st,n in pc.items():
            if lc[st]>=n or st in('}','} else {','else {','{') or st.endswith(':'): continue
            others=[x for x in lc if x not in pc]
            if a not in lv[1] and a not in lv[2]: k='addr-block-absent'
            elif lhs(st) and any(lhs(x)==lhs(st) for x in others): k='rewritten-same-lhs'
            elif st.startswith('goto') or st.startswith('if'): k='control-replaced'
            elif others: k='other-stmt-at-addr'
            else: k='bare-drop'
            kinds[k]+=1; ex[k].append(f'{name} {lf} 0x{a} | {st} || live: {" ;; ".join(others)[:150]}')
print(kinds)
for k in ex:
    print('==',k)
    for e in ex[k][:int(sys.argv[1]) if len(sys.argv)>1 else 8]: print('  ',e[:260])
