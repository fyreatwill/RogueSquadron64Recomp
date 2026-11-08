#!/usr/bin/env python3
# s7001 G5b: classify outer-ring (ring 7) dips of a ROGUESQ_DD_FWDWIN=tog run, per parity (seamless, as g5b_fwdwin_seamless.py).
# usage: g5b_ring7_discrim.py <dir> <arm> [ring=7]
# Per dip: heading distance to nearest diagonal (45+90k), window w/h, window edge on the pre-clamp bound (site 13),
# ring ref median. Baseline = same stats over all swaps of that parity, so a cluster shows as dip share >> base share.
import re,sys,math,statistics as st,struct,os
os.chdir(sys.argv[1]); nm=sys.argv[2]; RG=int(sys.argv[3]) if len(sys.argv)>3 else 7
sg=lambda x:(int(x)-(1<<32) if int(x)>>31 else int(x))
site=set();Q={}
for l in open('g3e_%s.txt'%nm,errors='replace'):
    r=l.split()
    if len(r)!=7: continue
    if r[2]=='15': site.add(int(r[1]))
    if r[2]=='13': Q[int(r[1])]=tuple(sg(x) for x in r[3:7])
S=[];last=None;pos=0
for l in open('tg_%s.txt'%nm,errors='replace'):
    if l[:2]!='S ' or ' hq=' not in l: continue
    p=l.split(); m=re.search(r'n=(\d+) m2=(\d+).* a=(-?\d+),(-?\d+) b=(-?\d+),(-?\d+) v0=\S+ win=(\S+) ',l)
    if not m: continue
    h=[int(x) for x in l.split(' hq=')[1].strip().rstrip(',').split(',')]; c=re.search(r'cam=(\S+)',l).group(1).split(',')
    t=int(p[2]); sec=t//24000000; pos=pos+1 if sec==last else 0; last=sec
    if int(m[2])<300 or pos<2: continue
    fx,fz=float(c[2]),float(c[8])
    if fx*fx+fz*fz<.2: continue
    hd=math.degrees(math.atan2(fz,fx))%360; dg=abs(((hd-45)%90)-45)  # 0 = on a diagonal, 45 = on an axis
    k=int(p[1]); w=[int(x) for x in m[7].split(',')]; q=Q.get(k) or Q.get(k-1)
    edge=None
    if q: edge=(w[0]<=q[0])+(w[0]+w[1]>=q[1])+(w[2]<=q[2])+(w[2]+w[3]>=q[3])
    S.append(dict(k=k,par=sec&1,h=h,dg=dg,ww=w[1],wh=w[3],edge=edge,sq=(w[1]>=60 and w[3]>=60)))
def summ(nm2,v):
    if not v: return '%s n=0'%nm2
    e=[x['edge'] for x in v if x['edge'] is not None]
    return '%s n=%d diag<15 %.2f axis>30 %.2f sq64 %.2f edge>0 %.2f w/h p50 %d/%d'%(nm2,len(v),sum(x['dg']<15 for x in v)/len(v),sum(x['dg']>30 for x in v)/len(v),sum(x['sq'] for x in v)/len(v),(sum(x>0 for x in e)/len(e)) if e else -1,st.median(x['ww'] for x in v),st.median(x['wh'] for x in v))
print(nm,'ring',RG,'swaps',len(S),'site13 rows',len(Q))
for par in (0,1):
    w=[s for s in S if s['par']==par and (s['k'] in site)==(par==1)]
    if len(w)<50: print(' parity',par,'n/a'); continue
    R=5; dips={60:[],120:[]}; refs=[]
    for i in range(R,len(w)-R):
        r2=st.median([x['h'][RG] for x in w[i-R:i]+w[i+1:i+R+1]]); refs.append(r2)
        for th in dips:
            if r2>=th and w[i]['h'][RG]<.5*r2: dips[th].append(dict(w[i],ref=r2))
    lab='armed' if par else 'off  '
    print(' %s %s'%(lab,summ('ALL',w)))
    print(' %s %s ref p50 %.0f'%(lab,summ('DIP60',dips[60]),st.median([d['ref'] for d in dips[60]]) if dips[60] else 0))
    print(' %s DIP120 n=%d  ring%d p50 all %.0f  ref>=60 share %.2f'%(lab,len(dips[120]),RG,st.median(x['h'][RG] for x in w),sum(r>=60 for r in refs)/len(refs)))
    # dip rate per diagonal-distance bin
    bins=[(0,15),(15,30),(30,46)]
    out=[]
    for a,b in bins:
        idx=[i for i in range(R,len(w)-R) if a<=w[i]['dg']<b]
        dd=sum(1 for d in dips[60] if a<=d['dg']<b)
        out.append('dg%d-%d %d/%d'%(a,b,dd,len(idx)))
    print('  ',lab,' '.join(out))
