#!/usr/bin/env python3
"""s6933: same-run pixel score of two toggles on a static scene. Captures c_<epoch>.png. Toggle A: (epoch/10)&1 (ROGUESQ_WRAP_MERGE=tog). Toggle B: 4 s
blocks of mach_absolute_time (ROGUESQ_DD_FOG=tog), read from CLOCK_UPTIME_RAW (24 MHz ticks, must score while the host has not slept since the run).
Pairs within --win seconds, classed: floor (same A, same B), test (A differs, B same), control (A same, B differs). Control must sit above floor or a null on test says nothing.
usage: g1e_tog_px.py DIR [--win 40] [--crop 62]"""
import sys, os, re, time, argparse, statistics as st
from PIL import Image, ImageChops, ImageStat
ap=argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--win',type=float,default=40); ap.add_argument('--crop',type=int,default=62); a=ap.parse_args()
off=time.time()-time.clock_gettime(time.CLOCK_UPTIME_RAW)
F=[]
for n in sorted(os.listdir(a.dir)):
    m=re.match(r'c_(\d+)\.png$',n)
    if not m: continue
    e=int(m[1]); i=Image.open(os.path.join(a.dir,n)).convert('L'); i=i.crop((0,a.crop,i.width,i.height)).resize((i.width//2,(i.height-a.crop)//2))
    F.append((e,(e//10)&1,int((e-off)//4)&1,i))
print('frames',len(F),'A on',sum(f[1] for f in F),'B on',sum(f[2] for f in F))
C={'floor':[],'test':[],'control':[]}
for x in range(len(F)):
    for y in range(x+1,len(F)):
        p,q=F[x],F[y]
        if q[0]-p[0]>a.win: continue
        k='floor' if p[1]==q[1] and p[2]==q[2] else 'test' if p[2]==q[2] else 'control' if p[1]==q[1] else None
        if not k: continue
        d=ImageChops.difference(p[3],q[3]); h=d.histogram(); n=sum(h)
        C[k].append((ImageStat.Stat(d).mean[0],sum(h[9:])/n*100))
for k,v in C.items():
    if v: print('%-8s pairs %3d  mean abs p50 %.3f max %.3f   px>8 %% p50 %.3f max %.3f'%(k,len(v),st.median(x[0] for x in v),max(x[0] for x in v),st.median(x[1] for x in v),max(x[1] for x in v)))
    else: print(k,'no pairs')
