#!/usr/bin/env python3
"""s6934: same-run rate of a =tog arm ((epoch/10)&1 on). [g1b] t counts from game start, so epoch = log file birth time + t + SKEW; seconds within 2 of a flip are dropped
so ~1 s of skew cannot mix blocks. usage: g1e_tog_rate.py log [from_t=100] [skew=0]"""
import os,re,statistics as st,subprocess,sys
f=sys.argv[1]; t0=int(sys.argv[2]) if len(sys.argv)>2 else 100; sk=int(sys.argv[3]) if len(sys.argv)>3 else 0
b=int(subprocess.check_output(['/usr/bin/stat','-f','%B',f]))
G=re.compile(rb'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/')
r={0:[],1:[]}
for l in open(f,'rb'):
    m=G.match(l)
    if not m or int(m[1])<t0: continue
    e=b+int(m[1])+sk
    if 2<=e%10<=7: r[(e//10)&1].append((int(m[3]),float(m[4])))
for k in (0,1):
    v=r[k]
    if v: print('on' if k else 'off','secs',len(v),'tasks/s %.1f'%st.mean(x[0] for x in v),'sd_wall mean %.2f p50 %.2f'%(st.mean(x[1] for x in v),st.median(x[1] for x in v)))
