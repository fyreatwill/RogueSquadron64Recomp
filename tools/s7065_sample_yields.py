#!/usr/bin/env python3
"""s7065: per 1-s host sample of the game MAIN thread, split samples into OS-wait (do_recv), yield_self_1ms by guest caller, and on-CPU.
Aligns files to G1E_TL gaps (>150 ms between game-thread osViSwapBuffer) by fitting a clock offset; prints per-gap-overlapping file rows.
usage: run from the outdir of tools/s7065_sample_loop.zsh, which also holds the G1E_TL ring (tl_*.bin.*). Clock: python time.monotonic == the TL steady clock (s7065 fit 0.23 s, +-3 s controls 0)."""
import re,glob,collections,struct,sys
def mainrows(fn):
    out=False; rows=[]
    for l in open(fn,errors='replace'):
        if re.match(r'^\s+\d+ Thread_\d+',l):
            if out: break
            out='[Game] MAIN' in l; continue
        if out:
            if not l.strip(): break
            m=re.match(r'^([\s+!:|]*)(\d+)\s+(.*?)(?:\s+\(in |\s+\[0x|$)',l)
            if m: rows.append((len(m.group(1)),int(m.group(2)),m.group(3).strip()))
    return rows
def classify(rows):
    c=collections.Counter(); stack=[]
    for i,(d,n,name) in enumerate(rows):
        while stack and stack[-1][0]>=d: stack.pop()
        stack.append((d,name))
        j=i+1
        while j<len(rows) and rows[j][0]>d: j+=1
        dk=rows[i+1:j]; kids=sum(r[1] for r in dk if r[0]==min(x[0] for x in dk)) if dk else 0
        s=n-kids
        if s<=0: continue
        nm=[x[1] for x in stack]
        if 'yield_self_1ms' in nm:
            k=nm.index('yield_self_1ms'); c['Y:'+nm[k-1]]+=s
        elif any(x.startswith('do_recv') for x in nm): c['R:'+(nm[[x.startswith('osRecvMesg_recomp') for x in nm].index(True)-1] if 'osRecvMesg_recomp' in nm else '?')]+=s
        elif any('semaphore' in x or 'wait_for_resumed' in x for x in nm): c['W:'+'/'.join(x for x in nm if not x.startswith(('std','_','thread','run_thread','main','DYLD')))[-90:]]+=s
        else: c['C']+=s
    return c
log=open('smp_log.txt').read().split('\n'); st={}
k=0
for l in log:
    p=l.split()
    if len(p)==2 and not l.startswith('end'): k+=1; st[k]=float(p[1])
fs={int(re.findall(r'smp_(\d+)',f)[0]):f for f in glob.glob('smp_[0-9]*.txt')}
data={i:classify(mainrows(f)) for i,f in fs.items()}
tot=collections.Counter()
for c in data.values(): tot.update(c)
print('TOTAL over',len(data),'s:'); [print(f'   {n:7d} {k}') for k,n in tot.most_common(14)]
raw=open(glob.glob('tl_*.bin.*')[0],'rb').read(); ev=sorted(struct.unpack_from('<qIIii',raw,i*24) for i in range(len(raw)//24)); ev=[e for e in ev if e[0]]
sw=[e[0]/1e6 for e in ev if e[1]==15 and e[4]==8]; gaps=[(a,b) for a,b in zip(sw,sw[1:]) if b-a>0.15]
Y={i:sum(v for k,v in c.items() if k.startswith('Y:')) for i,c in data.items()}
def score(off): return sum(Y[i] for i in data if any(a<st[i]+off+1 and b>st[i]+off for a,b in gaps))
base=gaps[0][0]-st[min(data)] if gaps else 0
cands=[(score(base+o/20),base+o/20) for o in range(-20*400,20*400)]
best=max(cands); print('gaps',len(gaps),'offset fit',best, 'controls +-3s', score(best[1]+3),score(best[1]-3))
off=best[1]
for a,b in gaps:
    ov=[i for i in data if st[i]+off<b and st[i]+off+1>a]
    s=' '.join(f'{k}={v}' for i in ov for k,v in data[i].most_common(5) if k.startswith('Y'))
    print(f'gap @{a-sw[0]:6.1f}s {1000*(b-a):4.0f}ms files={ov} {s[:200]}')
