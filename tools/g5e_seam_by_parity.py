#!/usr/bin/env python3
"""s6920: per 1 s DD_CUT_LIVE parity (col 8), same method as s6904 seam.py: alpha just past the 0055->C811 seam, seam z, tris/swap, and the cutoff the chain read (col 9).
Swaps whose rows straddle a parity change are dropped."""
import sys,struct,statistics as S,collections
fl=lambda w:struct.unpack('>f',bytes.fromhex(w))[0]
for f in sys.argv[1:]:
    sw=collections.defaultdict(lambda:{'a':[], 'b':[], 'p':set(), 'c':set()})
    for l in open(f,errors='replace'):
        p=l.split()
        if len(p)<10 or len(p[9])!=8: continue
        try: z=int(p[3],16)/65536; a=int(p[4]); s=int(p[0]); par=int(p[8]); c=p[9]
        except: continue
        d=sw[s]; d['p'].add(par); d['c'].add(c)
        if p[1]=='C8112220': d['b'].append((z,a))
        elif p[1]=='00552220': d['a'].append(z)
    print(f.split('/')[-1],'sampled swaps',len(sw),'straddle',sum(len(d['p'])>1 for d in sw.values()))
    for par in (0,1):
        n=[];c=[];u=[];zb=[];ab=[];ad=[];cut=collections.Counter();hi=0
        for s,d in sw.items():
            if d['p']!={par} or not d['b']: continue
            n.append(len(d['a'])+len(d['b'])); c.append(len(d['b'])); u.append(len(d['a']))
            b=sorted(d['b']); k=max(1,len(b)//20)
            x=S.median(max(0,min(255,q[1])) for q in b[:k]); ab.append(x); hi+=x>16
            ad.append(S.median(max(0,min(255,q[1])) for q in b[k:len(b)//2+1] or b))
            if d['a']:
                zz=sorted(d['a']); zb.append(zz[len(zz)*98//100])
            for w in d['c']:
                if len(w)==8: cut[round(fl(w),1)]+=1
        if not n: print(' ',par,'no swaps'); continue
        ab.sort()
        print('  %s swaps %4d tris %5.0f (C811 %5.0f 0055 %5.0f) seam z %.1f a@seam p50 %3d p90 %3d n>16 %d  mid p50 %3d  cut %s'%('live   ' if par else 'latched',len(n),S.mean(n),S.mean(c),S.mean(u),S.median(zb) if zb else 0,S.median(ab),ab[len(ab)*9//10],hi,S.median(ad),cut.most_common(4)))
