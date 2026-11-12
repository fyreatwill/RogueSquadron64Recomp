# s7188: per-native-column mean |d| (presented crop resized to the AL fb size vs the angrylion replay), edge columns vs median.
# usage: colprof.py dir name rect sub lo hi [label]
import sys,csv; sys.path.insert(0,'tools'); import s7122_fidelity as F
from PIL import Image
D,N,R,sub,lo,hi=sys.argv[1:7]; R=tuple(map(int,R.split(','))); lo,hi=int(lo),int(hi); raw=F.Raw('%s/%s.raw'%(D,N))
rows=[r for r in csv.DictReader(open('%s/%sC.frames.csv'%(D,N))) if lo<=int(r['swap'])<=hi][::6][:10]
acc=None;n=0;aledge=None
for r in rows:
    al=F.load_al('%s/%s%s/f%s.rgb'%(D,N,sub,r['swap']))
    if al is None: continue
    W,H=al.size; pr=raw.img(int(r['pframe'])).crop(R).resize((W,H),Image.BOX)
    a=al.convert('L').load(); b=pr.convert('L').load()
    col=[sum(abs(a[x,y]-b[x,y]) for y in range(0,H-8))/(H-8) for x in range(W)]
    alc=[sum(a[x,y] for y in range(0,H-8))/(H-8) for x in range(W-4,W)]; prc=[sum(b[x,y] for y in range(0,H-8))/(H-8) for x in range(W-4,W)]
    acc=col if acc is None else [p+q for p,q in zip(acc,col)]; n+=1
acc=[v/n for v in acc]; s=sorted(acc)
print(N,sys.argv[7] if len(sys.argv)>7 else '', 'W',len(acc),'med %.2f'%s[len(s)//2],'L',['%.1f'%v for v in acc[:3]],'R',['%.1f'%v for v in acc[-4:]],'| last frame AL lum',['%.0f'%v for v in alc],'pres lum',['%.0f'%v for v in prc])
