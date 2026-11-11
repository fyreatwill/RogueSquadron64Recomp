#!/usr/bin/env python3
# s7154 (from s7153; env CROP=x0,y0,x1,y1 ALSUF=c|n, kmd env BOXES=name=x0:y0:x1:y1;...) s7153 helper (kmd). Run from the capture dir (e.g. scratch/s7153); phsheet: D env = dir, args name [k a0 a1]; kmd: name joined.csv sx sy e; kgrid: name joined.csv [boxes]
import sys,csv,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import s7122_fidelity as F
from PIL import Image
N,J,sx,sy,e=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]); raw=F.Raw(N+'.raw'); R=tuple(map(int,os.environ.get('CROP','0,11,469,216').split(','))); W,H=R[2]-R[0],R[3]-R[1]; Q=4
rows=list(csv.DictReader(open(J)))[::8][:8]
fr=[(F.load_al(('%s'+os.environ.get('ALSUF','c')+'/f%s.rgb')%(N,r['swap'])).resize((W*Q,H*Q),Image.BOX),raw.img(int(r['pframe'])).crop(R)) for r in rows]
K=(0.99,0.995,1.0,1.005,1.01,1.015)
B=dict((q.split('=')[0],tuple(map(int,q.split('=')[1].split(':')))) for q in os.environ['BOXES'].split(';')) if os.environ.get('BOXES') else {'ringL(tri)':(118,20,150,190),'ringR(tri)':(320,20,351,190),'text':(140,60,330,150),'title':(140,4,330,60)}
for nm,b in B.items():
    out=[]
    for k in K:
        cx=W/2*Q; t=[]
        for a4,p in fr:
            a=a4.transform(a4.size,Image.AFFINE,(1/k,0,cx-cx/k-sx,0,e,-sy),Image.BILINEAR).resize((W,H),Image.BOX)
            d=F.dmap(a.crop(b),p.crop(b)); t.append(sum(d)/len(d))
        out.append(sorted(t)[len(t)//2])
    print('%-11s'%nm,' '.join('k%.3f=%.2f'%(k,v) for k,v in zip(K,out)),' best k %.3f'%K[out.index(min(out))])
