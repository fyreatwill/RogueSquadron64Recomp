#!/usr/bin/env python3
"""s7643: bucket TSan data-race reports by unordered FUNCTION pair (first non-runtime frame of each access, addresses stripped)
plus location kind/global name, and the two threads' creation roles. Usage: s7643_tsan_pairs.py <tsan files...>"""
import sys,re,collections
SKIP=re.compile(r'__tsan|libclang_rt|libsystem|std::__1::|operator new|memcpy|memmove|memset|_platform_|^<null>$')
def fn(sec):
    for l in sec:
        m=re.match(r'\s+#\d+ (.*?) (<null>|\S+:\d+|\(\S+\+0x[0-9a-f]+\))',l)
        if m and not SKIP.search(m.group(1)): return re.sub(r'\(.*','',m.group(1)).strip()[:60]
    return '?'
B=collections.Counter()
for p in sys.argv[1:]:
    txt=open(p,errors='replace').read()
    for rep in txt.split('WARNING: ThreadSanitizer: data race')[1:]:
        rep=rep.split('SUMMARY:')[0]; L=rep.splitlines(); secs=[]; cur=None
        for l in L:
            if re.match(r'\s*(Write|Read|Previous write|Previous read|Atomic \w+|Previous atomic \w+) of size',l): cur=[];secs.append(cur)
            elif re.match(r'\s*(Location is|Mutex|Thread |Issue)',l) or not l.strip(): cur=None
            elif cur is not None: cur.append(l)
        loc=next((l for l in L if 'Location is' in l),'')
        g=re.search(r"global '([^']+)'",loc); loc= g.group(1)[:40] if g else ('heap' if 'heap' in loc else ('stack' if 'stack' in loc else 'unk'))
        ths=re.findall(r'(?:Write|Read|write|read) of size \d+ at 0x[0-9a-f]+ by (main thread|thread T\d+)',rep)[:2]
        roles=[]
        for th in ths:
            if th=='main thread': roles.append('main'); continue
            m=re.search(r'Thread '+th.split()[-1]+r' \(.*?created by .*? at:\n(.*?)\n\n',rep+'\n\n',re.S)
            r='?'
            if m:
                for l in m.group(1).splitlines()[1:]:
                    f=re.sub(r'^\s+#\d+ ','',l)
                    if f.startswith(('std::','pthread','void* std')): continue
                    r=re.sub(r'\(.*','',f).strip()[:40]; break
            roles.append(r)
        a=tuple(sorted(zip((fn(s) for s in secs[:2]),roles))); B[tuple(f"{x}[{y}]" for x,y in a)+(loc,)]+=1
for k,v in B.most_common(): print(f"{v:4d} | {k[0]} <-> {k[1]} | {k[2]}")
print(f"pairs={len(B)} reports={sum(B.values())}")
