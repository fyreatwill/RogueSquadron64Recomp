import collections,pathlib,re,sys
L=pathlib.Path('../N64Recomp/RecompiledFuncs'); S=pathlib.Path('../N64Recomp/scratch_s6863_replay')
norm=lambda x: re.sub(r'\s+','',x)
lo=collections.Counter(); so=collections.Counter(); ex={}
allL=[];allS=[]
for f in sorted(L.iterdir()):
    if not f.is_file(): continue
    a=collections.Counter(norm(x) for x in f.read_text(errors='surrogateescape').split('\n'))
    b=collections.Counter(norm(x) for x in (S/f.name).read_text(errors='surrogateescape').split('\n')) if (S/f.name).exists() else collections.Counter()
    raw={norm(x):x for x in f.read_text(errors='surrogateescape').split('\n')}
    rawS={norm(x):x for x in (S/f.name).read_text(errors='surrogateescape').split('\n')} if (S/f.name).exists() else {}
    for k,v in (a-b).items(): allL.append((f.name,raw[k],v))
    for k,v in (b-a).items(): allS.append((f.name,rawS[k],v))
def tag(l):
    m=re.search(r'PATCH: (s\d+\w*)',l) or re.search(r'\b(rs\d{4}|rs64_s\d+|s\d{4})\w*',l)
    if m: return m.group(1)
    if re.fullmatch(r'[\s;{}]*',l): return '(blank/brace)'
    if '// 0x' in l: return '(asm comment)'
    return '(untagged)'
for name,rows in (('LIVE-ONLY',allL),('SCRATCH-ONLY',allS)):
    c=collections.Counter()
    for f,l,v in rows: c[tag(l)]+=v
    print(name,sum(c.values()),c.most_common(24))
    print('  by file',collections.Counter(f for f,l,v in rows).most_common(8))
import json; json.dump({'live':allL,'scr':allS},open('scratch/s6863/resid.json','w'))
