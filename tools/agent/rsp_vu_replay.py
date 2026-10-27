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
# s6380: reads [spike-vu8] (all 8 lanes of vs/vte/ACC pre-state + post-op vd result).
rows=[]
for l in open(sys.argv[1],errors='replace').read().split('\n')[int(sys.argv[2])-1:]:
    m=re.match(r'\[spike-vu8\] (\w+) vd=v(\d+) vs=(\S+) vte=(\S+) H=(\S+) M=(\S+) L=(\S+) pvd=(\S+) post=(\S+)',l)
    if m:
        f=lambda x:[int(v,16) for v in x.split(',')]
        rows.append(dict(n=m[1],vd=int(m[2]),vs=f(m[3]),vt=f(m[4]),H=f(m[5]),M=f(m[6]),L=f(m[7]),pvd=f(m[8]),post=f(m[9])))
    elif rows and not l.startswith('[spike-vu'): break
okA=badA=okR=badR=skip=sat=0
for i in range(len(rows)-1):
    a,b=rows[i],rows[i+1]
    for ln in range(8):
        pre=(a['H'][ln]<<32)|(a['M'][ln]<<16)|a['L'][ln]
        r=op(a['n'],pre,a['vs'][ln],a['vt'][ln])
        if r is None: skip+=1; continue
        acc,res=r
        if b['n'].startswith('VMAD') or b['n']=='VMACF':
            want=(b['H'][ln]<<32)|(b['M'][ln]<<16)|b['L'][ln]
            if s48(want)==acc: okA+=1
            else: badA+=1; print(f'ACC row{i} lane{ln} {a["n"]} s={a["vs"][ln]:04X} t={a["vt"][ln]:04X} model={acc&(2**48-1):012X} logged={want&(2**48-1):012X}')
        if res is not None:
            if res==a['post'][ln]:
                okR+=1
                if res in (0x7FFF,0x8000,0xFFFF,0x0000) and (s48(acc)>>16 > 0x7FFF or s48(acc)>>16 < -0x8000): sat+=1
            else: badR+=1; print(f'RES row{i} lane{ln} {a["n"]} s={a["vs"][ln]:04X} t={a["vt"][ln]:04X} acc={acc&(2**48-1):012X} model_vd={res:04X} logged_post={a["post"][ln]:04X}')
print(f'rows={len(rows)} accMatch={okA} accMismatch={badA} resMatch={okR} resMismatch={badR} saturatedResMatch={sat} skipped={skip}')
