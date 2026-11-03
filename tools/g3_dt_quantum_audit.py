#!/usr/bin/env python3
"""s6818 G3 FPS60 idiom audit: every caller of the axis-rotate helpers 0x8001CC3C / 0x8001CD6C (angle in $a1), with a
linear backward slice of $a1 (depth 3) to classify the angle source: object field (lw/lwc1 off a base), rodata constant,
or an incoming float argument (the dt arg in tick functions) multiplied in. A per-event K*dt step (s6817 collision
resolver 0x800FEF10) shows as 'mul.s ... <?$fN from entry/arg' with a rodata factor. Linear scan, ignores branches - a
triage list, read the flagged sites by hand.
Usage: g3_dt_quantum_audit.py [RecompiledFuncs dir] [--slice]"""
import re, glob, sys
R = next((a for a in sys.argv[1:] if not a.startswith('--')), '../N64Recomp/RecompiledFuncs')
funcs={}
for p in glob.glob(R+'/funcs_*.c'):
    fn=None
    for ln in open(p):
        m=re.match(r'RECOMP_FUNC void (\w+)\(',ln)
        if m: fn=m.group(1); funcs[fn]=[]
        m=re.match(r'\s*// (0x[0-9A-F]+): (.*)',ln)
        if m and fn: funcs[fn].append((m.group(1),m.group(2).strip()))
for fn,asm in sorted(funcs.items()):
    calls=[i for i,(a,t) in enumerate(asm) if re.match(r'jal\s+0x8001C(C3C|D6C)',t)]
    if not calls: continue
    dt=[a for a,t in asm if '-0x56FC' in t]
    print('%-40s calls=%d dtloads=%d %s'%(fn,len(calls),len(dt),' '.join(dt[:4])))

def defs(t):
    m=re.match(r'(\S+)\s+(.*)',t)
    if not m: return None,[],t
    op,args=m.group(1),[x.strip() for x in m.group(2).split(',')]
    if op in('mtc1',): return args[1],[args[0]],op
    if op.startswith(('sw','sd','sb','sh','swc1','sdc1','j','b','c.','nop')): return None,[],op
    if op in('swc1','sdc1'): return None,[],op
    if not args: return None,[],op
    d=args[0]
    srcs=[re.sub(r'.*\((\$\w+)\)',r'\1',a) for a in args[1:]]
    if op in('lwc1','lw','ldc1'): return d,[t],op
    if op=='lui': return d,['lui '+args[1]],op
    return d,[s for s in srcs if s.startswith('$')],op
def slice_(asm,i,reg,depth,seen):
    out=[]
    for k in range(i-1,max(0,i-60),-1):
        a,t=asm[k]
        d,srcs,op=defs(t)
        if d==reg:
            out.append(t)
            if depth>0 and op not in('lwc1','lw','ldc1','lui'):
                for s in srcs:
                    if s.startswith('$') and s not in('$zero',) and (s,k) not in seen:
                        seen.add((s,k)); out+=['  '*(4-depth)+'<'+x for x in slice_(asm,k,s,depth-1,seen)]
            return out
    return ['?'+reg+' from entry/arg']
if '--slice' in sys.argv:
  for fn,asm in sorted(funcs.items()):
    for i,(a,t) in enumerate(asm):
        if re.match(r'jal\s+0x8001C(C3C|D6C)',t):
            # delay slot may set a1
            ds=asm[i+1][1]
            print('==',fn,a,t[-4:],'| ds:',ds)
            sub=asm[:i+2] if defs(ds)[0]=='$a1' else asm[:i]
            for x in slice_(asm,len(sub) if defs(ds)[0]=='$a1' else i,'$a1',3,set())[:8]: print('   ',x)
