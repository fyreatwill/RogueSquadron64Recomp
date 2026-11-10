#!/usr/bin/env python3
"""s7059: classify game-thread xctrace samples inside each G1E_TL-ring stall (>150 ms between game-thread osViSwapBuffer marks).
The trace-to-ring offset is fitted by maximising samples-in-stalls over 140-200 s (printed with +-1 s controls, which must be far lower).
usage: g5e_stall_split.py <xctrace time-profile export.xml> "<tl.bin.pid glob>"   (game slot 8; edit cat() for new classes)"""
import sys,struct,glob,collections,xml.etree.ElementTree as ET
xmlp,tlp=sys.argv[1],sys.argv[2]
ids={}; rows=[]
for ev,e in ET.iterparse(xmlp,events=('end',)):
    i=e.get('id')
    if i: ids[i]=e
    if e.tag!='row': continue
    t=th=None; fl=[]
    for c in e:
        r=ids.get(c.get('ref'),c) if c.get('ref') else c
        if c.tag=='sample-time': t=int(r.text)
        elif c.tag=='thread': th=r.get('fmt')
        elif c.tag=='tagged-backtrace':
            b=r.find('backtrace'); b=ids.get(b.get('ref'),b) if b is not None and b.get('ref') else b
            if b is not None:
                for f in b.findall('frame'):
                    f=ids.get(f.get('ref'),f) if f.get('ref') else f; fl.append(f.get('name','?'))
    if 'MAIN' in th: rows.append((t/1e9,fl))
raw=open(glob.glob(tlp)[0],'rb').read(); ev=sorted(struct.unpack_from('<qIIii',raw,i*24) for i in range(len(raw)//24)); ev=[e for e in ev if e[0]]
t0=ev[0][0]; sw=[e[0] for e in ev if e[1]==15 and e[4]==8]
gaps=[((a-t0)/1e6,(b-t0)/1e6) for a,b in zip(sw,sw[1:]) if b-a>150000]
ts=[r[0] for r in rows]
import bisect
def score(off): return sum(bisect.bisect_left(ts,b-off)-bisect.bisect_left(ts,a-off) for a,b in gaps)
best=max((score(o/100),o/100) for o in range(14000,20000,2)); off=best[1]
print(f'offset={off:.2f}s samples-in-stalls={best[0]} (shift+1s: {score(off+1)}, -1s: {score(off-1)})')
def cat(fl):
    s=' '.join(fl)
    if 'AudioSlotActive' in s or 'waitForAnyAudioSlot' in s: return 'audio-slot-poll'
    if 'rasterizeFormatMessageGlyphs' in s or 'decodeBackdropTilesToTextures' in s or 'buildDebrisMesh' in s: return 'text-glyph-build'
    if 'semaphore' in fl[0] or 'wait' in fl[0]: return 'wait'
    return 'other'
tot=collections.Counter(); roots=collections.Counter()
for a,b in gaps:
    sel=[fl for t,fl in rows if a-off<=t<b-off]
    if not sel and not (ts[0]<=a-off<=ts[-1]): continue
    c=collections.Counter(cat(fl) for fl in sel); tot.update(c)
    for fl in sel:
        g=[x for x in fl if not x.startswith(('rs64_','std::','_','DYLD','0x','run_thread','mainBoot'))]
        roots[' < '.join(g[-4:])]+=1
    print(f'stall ring t={a:7.1f}s len={(b-a)*1000:5.0f}ms samples={len(sel):3d}', dict(c))
print('TOTAL', dict(tot)); print('outer callers:'); [print('  ',n,k[:200]) for k,n in roots.most_common(8)]
