#!/usr/bin/env python3
# s7007 G5e: far-terrain silhouette scorer for g5b_capture raws (16-byte header <QII mach,w,h + w*h RGB per frame; title bar rows 0-27).
# usage: g5e_edge_score.py raw [frame_step=2] [frame_limit] [step_threshold=50] [toggle_period_ticks=96e6]
# Per sampled column: topmost row >=150 where |c(y-3)-c(y+3)|_1 >= threshold and the 10 rows below are flat (luma range <=24).
# Binned by toggle parity (odd period = state 1; 24e6 for 1 s =tog levers, 96e6 for 4 s ones) and screen third; frames at period phase 0.15-0.85 only.
# hard80% = share of columns whose edge step is >= 80 (the fog-colour slab steps ~110; dd1 floor from clouds/ship/hills is 11-27%).
# per-column far silhouette: topmost y (rows 24..h-70) where the 10 px below are flat (luma range<=6) and the step |c(y-3)-c(y+3)|_1 >= TH.
# prints per fog state (and per third) : frames, columns with an edge (%), median step. frames must be in flight (side columns not black) and VI phase 0.15-0.85.
import sys,struct
raw=sys.argv[1]; step=int(sys.argv[2]) if len(sys.argv)>2 else 2; TH=int(sys.argv[4]) if len(sys.argv)>4 else 50; PER=float(sys.argv[5]) if len(sys.argv)>5 else 96e6; YMIN=150; lim=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
f=open(raw,'rb'); t,w,h=struct.unpack('<QII',f.read(16)); rec=16+w*h*3; n=min(f.seek(0,2)//rec,lim)
cols=[x for x in range(60,w-50,12)]
st={}
def L(b,o): return b[o]+2*b[o+1]+b[o+2]
for i in range(0,n,step):
    f.seek(i*rec); t,_,_=struct.unpack('<QII',f.read(16)); b=f.read(w*h*3)
    if sum(b[(200*w+x)*3] for x in (5,10,15))<30: continue   # debrief / letterboxed
    ph=(t/PER)%1
    if not 0.15<=ph<=0.85: continue
    fog=int(t//PER)&1
    for x in cols:
        y0=max(YMIN,230 if x>w-240 else (160 if x<100 else 36))
        hit=None
        for y in range(y0,h-70):
            o=(y*w+x)*3
            a=(y-3)*w*3+x*3; c=(y+3)*w*3+x*3
            s=abs(b[a]-b[c])+abs(b[a+1]-b[c+1])+abs(b[a+2]-b[c+2])
            if s<TH: continue
            ls=[L(b,((y+k)*w+x)*3) for k in range(3,13)]
            if max(ls)-min(ls)<=24: hit=s; break
        third=0 if x<w/3 else (1 if x<2*w/3 else 2)
        k=(fog,third); d=st.setdefault(k,[0,[]]); d[0]+=1
        if hit is not None: d[1].append(hit)
for fog in (0,1):
    for th in (0,1,2):
        d=st.get((fog,th),[0,[]]); v=sorted(d[1])
        print(f"fog={fog} third={th} cols={d[0]} edge%={100*len(v)/max(1,d[0]):.1f} med={v[len(v)//2] if v else 0} p90={v[int(len(v)*.9)] if v else 0} hard80%={100*sum(1 for q in v if q>=80)/max(1,d[0]):.1f}")
