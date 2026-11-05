#!/usr/bin/env python3
"""s6897 G5b: are TriGen bases map-absolute or eye-relative? Correlates each ROGUESQ_G5B_TG swap's base centre with the 12 cam floats
(0-8 view matrix, 9-11 position). Absolute: position terms high. Eye-relative: position ~0 and view terms ~1, which also serves as
the regression's positive control. usage: g5b_tg_camrel.py tg_x.txt [...]"""
import re,sys
A=sys.argv[1:]
def fit(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n; sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); syy=sum((y-my)**2 for y in ys)
    return (sxy/(sxx*syy)**.5 if sxx*syy>0 else 0)
for N in A:
    R=[]
    for l in open(N,errors='replace'):
        m=re.match(r'S (\d+) \d+ n=\d+ .* a=(-?\d+),(-?\d+) b=(-?\d+),(-?\d+) v0=\S+ win=\S+ deb4=\S+ tt=\S+ cam=(.*)',l)
        if not m: continue
        c=m[6].split(',')
        try: c=[float(v) for v in c[:12]]
        except: continue
        if len(c)<12 or c[9]==157.353 or c[10]==0: continue
        a0,a1,b0,b1=map(int,m.group(2,3,4,5))
        if a1-a0>40000 or b1-b0>40000: continue
        R.append(((a0+a1)/2,(b0+b1)/2,c))
    print(N,len(R))
    print('  r(a centre, c[i]):',' '.join('%+.2f'%fit([r[2][i] for r in R],[r[0] for r in R]) for i in range(12)))
    print('  r(b centre, c[i]):',' '.join('%+.2f'%fit([r[2][i] for r in R],[r[1] for r in R]) for i in range(12)))
