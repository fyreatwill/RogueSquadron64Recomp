#!/usr/bin/env python3
# s7153 helper (phsheet). Run from the capture dir (e.g. scratch/s7153); phsheet: D env = dir, args name [k a0 a1]; kmd: name joined.csv sx sy e; kgrid: name joined.csv [boxes]
import sys,csv,os; sys.path.insert(0,'tools'); import s7122_fidelity as F
from PIL import Image, ImageDraw
D=os.environ.get('D','scratch/s7153'); N=sys.argv[1]; R=(0,11,469,216); W,H=469,205
rows=list(csv.DictReader(open('%s/%sC.frames.csv'%(D,N)))); raw=F.Raw('%s/%s.raw'%(D,N))
k=int(sys.argv[2]) if len(sys.argv)>2 else 16; a0=int(sys.argv[3]) if len(sys.argv)>3 else 0; a1=int(sys.argv[4]) if len(sys.argv)>4 else 10**9
rows=[r for r in rows if a0<=int(r['swap'])<=a1]; pick=rows[::max(1,len(rows)//k)][:k]
sh=Image.new('RGB',(2*W,len(pick)*(H+12)),(30,30,30)); d=ImageDraw.Draw(sh)
for i,r in enumerate(pick):
    a=F.load_al('%s/%sc/f%s.rgb'%(D,N,r['swap'])); y=i*(H+12)
    sh.paste(raw.img(int(r['pframe'])).crop(R),(0,y+12))
    if a: sh.paste(a.resize((W,H)),(W,y+12))
    d.text((2,y),'swap %s frac %s'%(r['swap'],r['frac_over_T']),fill=(255,255,0))
sh=sh.resize((sh.width//2,sh.height//2)); sh.save('%s/ph_%s.png'%(D,N)); print(sh.size)
