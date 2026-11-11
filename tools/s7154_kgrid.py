#!/usr/bin/env python3
# s7154 (from s7153; env CROP=x0,y0,x1,y1 ALSUF=c|n, kmd env BOXES=name=x0:y0:x1:y1;...) s7153 helper (kgrid). Run from the capture dir (e.g. scratch/s7153); phsheet: D env = dir, args name [k a0 a1]; kmd: name joined.csv sx sy e; kgrid: name joined.csv [boxes]
import sys,csv,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import s7122_fidelity as F
from PIL import Image
N,J=sys.argv[1:3]; raw=F.Raw(N+'.raw'); R=tuple(map(int,os.environ.get('CROP','0,11,469,216').split(','))); W,H=R[2]-R[0],R[3]-R[1]; Q=4
rows=list(csv.DictReader(open(J)))[::8][:8]
fr=[(F.load_al(('%s'+os.environ.get('ALSUF','c')+'/f%s.rgb')%(N,r['swap'])).resize((W*Q,H*Q),Image.BOX),raw.img(int(r['pframe'])).crop(R)) for r in rows]
def sc(sx,sy,e,k,b):
    cx=W/2*Q; t=[]
    for a4,p in fr:
        a=a4.transform(a4.size,Image.AFFINE,(1/k,0,cx-cx/k-sx,0,e,-sy),Image.BILINEAR).resize((W,H),Image.BOX)
        d=F.dmap(a.crop(b),p.crop(b)); t.append(sum(v>F.T for v in d)/len(d))
    return sorted(t)[len(t)//2]
BX=[tuple([q.split("=")[0]]+[tuple(map(int,q.split("=")[1].split(":")))]) for q in sys.argv[3].split(";")] if len(sys.argv)>3 else [("top",(140,4,330,60)),("mid",(140,60,330,150)),("low",(140,150,330,200))]
for nm,b in BX:
    g={(sx,sy,e,k):sc(sx,sy,e,k,b) for sx in (0,1,2,3) for sy in (-2,0,2) for e in (0.996,0.992,0.988) for k in (0.99,0.995,1.0,1.005,1.01,1.333)}
    best=min(g,key=g.get); print(nm,'best',best,'%.4f'%g[best],'| k=1 best %.4f'%min(v for q,v in g.items() if q[3]==1.0),'| k=1.333 best %.4f'%min(v for q,v in g.items() if q[3]==1.333))
