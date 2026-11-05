#!/usr/bin/env python3
"""s6884: rate table for same-pose pinned arms (g3_optin_pose_arms.sh, dt pinned). The sim ticks between two [posefreeze] crossings are the
same work in every arm, so ticks / (wall - freeze) is a same-work game rate; [g1e-split] rows (1/s) inside the window give the spread.
usage: g1e_arm_rate.py <tagprefix> <arm> ...   reads scratch/agent/m6/g1_lvl1<tagprefix>_<arm>/run.log, rand.txt from --dir."""
import re,sys,argparse
ap=argparse.ArgumentParser(); ap.add_argument('tag'); ap.add_argument('arms',nargs='+'); ap.add_argument('--dir',default=None); ap.add_argument('--lvl',default='1'); ap.add_argument('--ms',type=int,default=4000)
a=ap.parse_args()
def pc(v,p): return sorted(v)[int(p*(len(v)-1))] if v else 0
print('arm | fast probes | log MB | k0-k2 VI (net) | ticks | tick fps | tasks min/p10/p50/p90 | s<50 | ucode p50/p90 | calls/task | ns/cmd | rows')
for arm in a.arms:
    L=f'scratch/agent/m6/g1_lvl{a.lvl}{a.tag}_{arm}/run.log'
    try: f=open(L,'rb')
    except OSError: print(arm,'no log'); continue
    fz=[];rows=[];size=0;fast=probes='?'
    for b in f:
        size+=len(b)
        if b.startswith(b'[posefreeze]'):
            m=re.search(rb'k=(\d+) vi=(\d+)',b); fz.append(int(m[2])); rows.append('F')
        elif b.startswith(b'[g1e-split]'):
            m=re.search(rb'phase=(\d+) spin=\d+ fast=(\d+) tasks=(\d+) ucode_ms=([\d.]+).*?calls=(\d+).*probes=(\d+)',b)
            if m and int(m[1])>=6:
                fast,probes=int(m[2]),int(m[6]); rows.append((int(m[3]),float(m[4]),int(m[5])))
    seg=[];s=0
    for r in rows:
        if r=='F': s+=1
        elif 1<=s<=(len(fz)-1 if fz else 0): seg.append(r)
    if not fz: seg=[r for r in rows if r!='F'][-70:]
    seg=[r for i,r in enumerate(seg)]
    tk=[r[0] for r in seg]; uc=[r[1] for r in seg]; ca=[r[2] for r in seg]
    net=fz[-1]-fz[0]-(len(fz)-1)*a.ms*60//1000 if len(fz)>1 else 0
    ticks=0
    if a.dir and len(fz)>1:
        try:
            xs=[]
            for b in open(f'{a.dir}/{arm}/rand.txt','rb'):
                if b' 800fa730 ' in b:
                    m=re.search(rb'm=80137dc0:([0-9a-f]{8})',b)
                    if m:
                        import struct; xs.append(struct.unpack('>f',bytes.fromhex(m[1].decode()))[0])
            i0=next(i for i,x in enumerate(xs) if x>=42.33); i2=next(i for i,x in enumerate(xs) if x>=106.28); ticks=i2-i0
        except (OSError,StopIteration): pass
    fps=ticks/(net/60) if net>0 and ticks else 0
    nscmd=1e6*pc(uc,.5)/max(pc(ca,.5),1)
    print(f'{arm} | {fast} {probes} | {size>>20} | {net} | {ticks} | {fps:.1f} | {min(tk,default=0)}/{pc(tk,.1)}/{pc(tk,.5)}/{pc(tk,.9)} | {sum(t<50 for t in tk)} | {pc(uc,.5):.1f}/{pc(uc,.9):.1f} | {pc(ca,.5)} | {nscmd:.0f} | {len(tk)}')
