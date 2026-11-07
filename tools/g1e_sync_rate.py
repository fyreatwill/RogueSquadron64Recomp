#!/usr/bin/env python3
"""s6933 G1e: per-arm split of the Gfx-thread budget from [g1b], [g1b-gt] and [g1e-aq], last N s of each log, by async state.
With --tog the first second after each flip is dropped. tasks*sd_wall + vi*us_wall = Gfx thread busy ms/s (g1e_gfxbusy.py).
H-overrun: sync task cost just above 16.7 ms. H-serial: well above. H-cadence: cost under 16.7 ms and tasks still ~30/s.
usage: g1e_sync_rate.py [--last 120] [--tog] log..."""
import re, sys, os, argparse, statistics as st
ap=argparse.ArgumentParser(); ap.add_argument('logs',nargs='+'); ap.add_argument('--last',type=int,default=120); ap.add_argument('--tog',action='store_true'); a=ap.parse_args()
G=re.compile(rb'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/(\d+) sd_cpu=([\d.]+)/(\d+) us_wall=([\d.]+)/(\d+).* as=(\d)')
T=re.compile(rb'^\[g1b-gt\] t=(\d+) sum_cpu=(\d+)(.*)')
A=re.compile(rb'^\[g1e-aq\] t=(\d+) as=(\d) n=(\d+) (.*)')
S=re.compile(rb'^\[g1e-scr\] t=(\d+) n=(\d+) drain=([\d.]+) pre=([\d.]+) up=([\d.]+) up_max=([\d.]+)')
pc=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else 0
for f in a.logs:
    g={}; gt={}; aq={}; sc={}
    for l in open(f,'rb'):
        if not l.startswith(b'[g1'): continue
        m=G.match(l)
        if m: g[int(m[1])]=dict(vi=int(m[2]),tk=int(m[3]),sw=float(m[4]),swm=int(m[5]),sc=float(m[6]),uw=float(m[8]),uwm=int(m[9]),a=int(m[10])); continue
        m=T.match(l)
        if m: gt[int(m[1])]=(int(m[2]),[x.split(b':') for x in m[3].split()]); continue
        m=A.match(l)
        if m: aq.setdefault(int(m[1]),{})[int(m[2])]=dict(n=int(m[3]),**{k.decode():float(v) for k,v in (x.split(b'=') for x in m[4].split())}); continue
        m=S.match(l)
        if m: sc[int(m[1])]=dict(drain=float(m[3]),up=float(m[5]))
    if not g: print(os.path.basename(f),'no g1b'); continue
    tmax=max(g); secs=[t for t in g if t>tmax-a.last and t<tmax]
    keys=sorted({g[t]['a'] for t in secs})
    for k in keys:
        ss=[t for t in secs if g[t]['a']==k and (not a.tog or g.get(t-1,{}).get('a')==k)]
        if not ss: continue
        R=[g[t] for t in ss]; busy=[r['tk']*r['sw']+r['vi']*r['uw'] for r in R]
        print('%s as=%d n=%d vi=%.1f tasks p10/50/90 %d/%d/%d sd_wall %.1f/%.1f/%.1f max %d sd_cpu %.1f us_wall %.1f/%.1f max %d busy p50 %.0f'%(os.path.basename(f),k,len(ss),st.mean(r['vi'] for r in R),
          pc([r['tk'] for r in R],.1),pc([r['tk'] for r in R],.5),pc([r['tk'] for r in R],.9),pc([r['sw'] for r in R],.1),pc([r['sw'] for r in R],.5),pc([r['sw'] for r in R],.9),max(r['swm'] for r in R),
          st.median(r['sc'] for r in R),pc([r['uw'] for r in R],.5),pc([r['uw'] for r in R],.9),max(r['uwm'] for r in R),st.median(busy)))
        qq={}
        for t in ss:
            for s,d in aq.get(t,{}).items():
                if d['n']>=5: qq.setdefault(s,[]).append(d)
        for s,v in sorted(qq.items()):
            print('   aq as=%d secs=%d n/s=%.1f '%(s,len(v),st.mean(d['n'] for d in v))+' '.join('%s=%.2f'%(c,st.median(d[c] for d in v)) for c in ('total','rsp','drain','wk','wk_tail','copy','sync_rt64','kB','jobs','calls')))
        z=[sc[t] for t in ss if t in sc]
        if z: print('   scr drain=%.2f up=%.2f'%(st.median(x['drain'] for x in z),st.median(x['up'] for x in z)))
        th={}
        for t in ss:
            for x in gt.get(t,(0,[]))[1]:
                c,b=x[1].split(b'/'); th.setdefault(x[0].decode(),[]).append((int(c),int(b)))
        top=sorted(th.items(),key=lambda kv:-st.mean(c for c,_ in kv[1]))[:5]
        print('   threads cpu/blk ms per s: '+' '.join('%s:%.0f/%.0f'%(n,st.median(c for c,_ in v),st.median(b for _,b in v)) for n,v in top))
