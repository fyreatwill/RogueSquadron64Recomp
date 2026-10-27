#!/usr/bin/env python3
"""Independent RSP VU lane-0 replay of the [spike-vu] ring (s6379).
Model written from the N64 RSP VU spec (48-bit acc, signed/unsigned clamps).
Usage: rsp_vu_replay.py run.log LINE   (LINE = first line of the ring dump)"""
import re, sys
def s16(x): x&=0xFFFF; return x-0x10000 if x&0x8000 else x
def s48(x): x&=(1<<48)-1; return x-(1<<48) if x>>47 else x
def clamp_s(acc):  # VMADH/VMUDH style: acc bits 47..16 clamp to s16
    hi = s48(acc)>>16
    return 0x7FFF if hi>0x7FFF else (0x8000 if hi<-0x8000 else s48(acc)>>0 & 0xFFFF) if False else None
def sat_signed(acc):
    a=s48(acc); m=a>>16
    if m>0x7FFF: return 0x7FFF
    if m<-0x8000: return 0x8000
    return (a>>16)&0xFFFF if True else 0
def sat_lo(acc):  # VMADN/VMUDN/VMUDL/VMADL clamp
    a=s48(acc); m=a>>16
    if m>0x7FFF: return 0xFFFF
    if m<-0x8000: return 0x0000
    return a&0xFFFF
def op(name,acc,s,t):
    s=s16(s); t=s16(t); su=s&0xFFFF; tu=t&0xFFFF
    if name=='VMUDH': acc=(s*t)<<16; r=sat_signed(acc)
    elif name=='VMADH': acc=s48(acc)+((s*t)<<16); r=sat_signed(acc)
    elif name=='VMUDN': acc=su*t; r=sat_lo(acc)
    elif name=='VMADN': acc=s48(acc)+su*t; r=sat_lo(acc)
    elif name=='VMUDM': acc=s*tu; r=sat_signed(acc)
    elif name=='VMADM': acc=s48(acc)+s*tu; r=sat_signed(acc)
    elif name=='VMUDL': acc=(su*tu)>>16; r=sat_lo(acc)
    elif name=='VMADL': acc=s48(acc)+((su*tu)>>16); r=sat_lo(acc)
    elif name=='VMULF': acc=s*t*2+0x8000; r=sat_signed(acc)
    elif name=='VMACF': acc=s48(acc)+s*t*2; r=sat_signed(acc)
    else: return None
    return s48(acc), r
rows=[]
for l in open(sys.argv[1],errors='replace').read().split('\n')[int(sys.argv[2])-1:]:
    m=re.match(r'\[spike-vu\] (\w+) vd=v(\d+) e=(\w+) vs1=(\w+) vte1=(\w+) preACC=(\w+)\.(\w+)\.(\w+)',l)
    if m: rows.append((m[1],int(m[4],16),int(m[5],16),(int(m[6],16)<<32)|(int(m[7],16)<<16)|int(m[8],16)))
    elif rows and not l.startswith('[spike-vu]'): break
ok=bad=skip=0
for i in range(len(rows)-1):
    n,s,t,pre=rows[i]; nxt=rows[i+1]
    r=op(n,pre,s,t)
    if r is None: skip+=1; continue
    acc,_=r
    if nxt[0].startswith('VMAD') or nxt[0] in ('VMACF',):
        want=s48(nxt[3]); got=s48(acc)
        if want==got: ok+=1
        else:
            bad+=1; print(f'row{i} {n} s={s:04X} t={t:04X} pre={pre&(2**48-1):012X} model={got&(2**48-1):012X} logged_next={want&(2**48-1):012X}')
    else: skip+=1
print(f'rows={len(rows)} match={ok} mismatch={bad} unchained/skipped={skip}')
