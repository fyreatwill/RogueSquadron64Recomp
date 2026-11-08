#!/usr/bin/env python3
# s7000 G5b: score a ROGUESQ_DD_FWDWIN=tog run from its ROGUESQ_G5B_TG + ROGUESQ_G3E_TRACE files.
# usage: g5b_fwdwin_seamless.py <dir> <arm>  (reads <dir>/tg_<arm>.txt and <dir>/g3e_<arm>.txt)
# Drops the first 2 swaps of each mach-second block: s7000 found every armed "dip" in a naive parity split sat on the
# first swap after the flip (x.4 s every 2 s). Armed = odd second AND site 15 fired; off = even second AND not fired.
import re,sys,math,statistics as st
import os; os.chdir(sys.argv[1]); nm=sys.argv[2]
site=set(int(l.split()[1]) for l in open('g3e_%s.txt'%nm,errors='replace') if len(l.split())==7 and l.split()[2]=='15')
S=[]; last=None; pos=0
for l in open('tg_%s.txt'%nm,errors='replace'):
    if l[:2]!='S ' or ' hq=' not in l: continue
    p=l.split(); m=re.search(r'n=(\d+) m2=(\d+).* a=(-?\d+),(-?\d+) b=(-?\d+),(-?\d+) v0=\S+ win=(\S+) ',l)
    if not m: continue
    h=[int(x) for x in l.split(' hq=')[1].strip().rstrip(',').split(',')]; c=re.search(r'cam=(\S+)',l).group(1).split(',')
    t=int(p[2]); sec=t//24000000; pos=pos+1 if sec==last else 0; last=sec
    if int(m[2])<300 or pos<2: continue
    fx,fz=float(c[2]),float(c[8]); hd=int((math.degrees(math.atan2(fz,fx))%360)//30) if fx*fx+fz*fz>=.2 else None
    a0,a1,b0,b1=map(int,m.group(3,4,5,6))
    S.append((int(p[1]),sec&1,int(m[1]),h,hd,max(abs(a0),abs(a1),abs(b0),abs(b1))/512,max(a1-a0,b1-b0)>40000))
print(nm,'in-flight swaps past the seam',len(S))
for par in (0,1):
    w=[s for s in S if s[1]==par and (s[0] in site)==(par==1)]
    if len(w)<50: print(' parity',par,'n/a',len(w)); continue
    n=[s[2] for s in w]; R=5; d=0; rc=[0]*8
    for i in range(R,len(w)-R):
        ref=st.median(n[i-R:i]+n[i+1:i+R+1])
        if ref>=200 and n[i]/ref<.8: d+=1
        for j in range(8):
            r2=st.median([x[3][j] for x in w[i-R:i]+w[i+1:i+R+1]])
            if r2>=60 and w[i][3][j]<.5*r2: rc[j]+=1
    sec={}
    for s in w:
        if s[4] is not None and not s[6]: sec.setdefault(s[4],[]).append(s)
    wv=min((sorted(x[2] for x in q)[len(q)//10],k) for k,q in sec.items() if len(q)>=30); q=sec[wv[1]]
    near=[s[3][0]+s[3][1] for s in w]
    print(f" {'armed' if par else 'off  '} swaps {len(w)} n p50 {st.median(n):.0f} worst hdg {wv[1]*30} p10 {wv[0]} reach p10 {sorted(x[5] for x in q)[len(q)//10]:.0f} dips<.8 {d} ring dips {rc} near p50 {st.median(near):.0f} near<50 {sum(x<50 for x in near)}")
