#!/usr/bin/env python3
"""s7642: bucket TSan data-race reports by (access-1 frame, access-2 frame, location). Usage: s7642_tsan_bucket.py <tsan files...>
Prints count per bucket with the first non-runtime frame of each access (skipping libc/tsan/std:: frames)."""
import sys,re,collections
SKIP=re.compile(r'__tsan|libclang_rt|libsystem|std::__1::|operator new|memcpy|memmove|memset|_platform_')
def frames(block):
    out=[]
    for l in block:
        m=re.match(r'\s+#\d+ (.*?) (\S+:\d+|\(\S+\+0x[0-9a-f]+\))',l)
        if m: out.append((m.group(1).strip(),m.group(2)))
    return out
def first(fr):
    for f,loc in fr:
        if not SKIP.search(f+loc): return f"{f[:90]} @{loc.split('/')[-1]}"
    return fr[0][0][:90] if fr else '?'
B=collections.Counter(); ex={}
for p in sys.argv[1:]:
    txt=open(p,errors='replace').read()
    for rep in txt.split('WARNING: ThreadSanitizer: data race')[1:]:
        rep=rep.split('SUMMARY:')[0]; L=rep.splitlines()
        secs=[];cur=None
        for l in L:
            if re.match(r'\s*(Write|Read|Previous write|Previous read|Atomic \w+|Previous atomic \w+) of size',l):
                cur=[l.strip().split(' by ')[0]+' T'+(re.search(r'thread (T\d+|main)',l) or re.search('(main)',l+'main')).group(1)];secs.append(cur)
            elif re.match(r'\s*(Location is|Mutex|Thread )',l): cur=None
            elif cur is not None: cur.append(l)
        loc=next((l.strip()[:80] for l in L if 'Location is' in l),'loc?')
        k=tuple(re.sub(r' at 0x[0-9a-f]+','',s[0]).split(' T')[0]+' :: '+first(frames(s[1:])) for s in secs[:2])+(re.sub(r'(at|thread) \S+','',loc),)
        B[k]+=1; ex.setdefault(k,p)
for k,v in B.most_common():
    print(f"{v:3d} | "+"\n    | ".join(k))
print(f"buckets={len(B)} reports={sum(B.values())}")
