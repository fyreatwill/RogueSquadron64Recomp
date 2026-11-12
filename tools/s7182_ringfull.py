# s7182: ring brightness at NATIVE fb resolution: RT64 full-res window capture box-downscaled to the AL fb size (both sides box
# filtered, no ScreenCaptureKit downscale). Ring box and wall control in fb coords; integer shift check; lit stats.
import sys,csv,importlib.util,statistics as S,collections
sp=importlib.util.spec_from_file_location('f','tools/s7122_fidelity.py');F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F)
from PIL import Image, ImageChops, ImageStat
D,RN,ALD,CSV,rect=sys.argv[1:6]; lo,hi=map(int,sys.argv[6].split(',')); rect=tuple(map(int,rect.split(','))); raw=F.Raw('%s/%s.raw'%(D,RN))
RING=(141,218,391,284); WALL=(16,87,133,204)
out=collections.defaultdict(list); fw={}; sh=collections.Counter()
for r in csv.DictReader(open(CSV)):
  s=int(r['swap'])
  if not (lo<=s<=hi) or int(r['pframe'])<=0: continue
  a=F.load_al('%s/%s/f%s.rgb'%(D,ALD,s))
  if a is None or a.size!=(512,339): continue
  p=raw.img(int(r['pframe'])).crop(rect).resize(a.size,Image.BOX)
  for nm,B in (('ring',RING),('wall',WALL)):
    A=a.crop(B).convert('L'); P=p.crop(B).convert('L'); out[nm+'_al'].append(ImageStat.Stat(A).mean[0]); out[nm+'_rt'].append(ImageStat.Stat(P).mean[0])
    if nm=='ring':
      ha=A.histogram(); hp=P.histogram(); out['lit_al'].append(sum(ha[193:])); out['lit_rt'].append(sum(hp[193:]))
      res=min((ImageStat.Stat(ImageChops.difference(p.crop((B[0]+dx,B[1]+dy,B[2]+dx,B[3]+dy)).convert('L'),A)).mean[0],dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)); sh[res[1:]]+=1
      ap=list(a.crop(B).getdata()); pp=list(p.crop(B).getdata())
      lit=[(x,y) for x,y in zip(ap,pp) if sum(x)/3>224]
      if lit: out['litrgb_al'].append([S.mean(q[0][i] for q in lit) for i in range(3)]); out['litrgb_rt'].append([S.mean(q[1][i] for q in lit) for i in range(3)])
      for x,y in zip(ap,pp): fw.setdefault(int(sum(x)/3)//32,[]).append(sum(y)/3-sum(x)/3)
      sa=sorted(A.getdata()); sp_=sorted(P.getdata()); out['p99_al'].append(sa[int(len(sa)*.99)]); out['p99_rt'].append(sp_[int(len(sp_)*.99)])
n=len(out['ring_al']); m=lambda k:S.mean(out[k]) if out[k] else float('nan')
print('swaps %d-%d n %d'%(lo,hi,n))
print('ring luma AL %.1f RT %.1f d %+.2f | wall AL %.1f RT %.1f d %+.2f'%(m('ring_al'),m('ring_rt'),m('ring_rt')-m('ring_al'),m('wall_al'),m('wall_rt'),m('wall_rt')-m('wall_al')))
print('lit>192 px AL %.0f RT %.0f | p99 luma AL %.1f RT %.1f | best shift %s'%(m('lit_al'),m('lit_rt'),m('p99_al'),m('p99_rt'),sh.most_common(3)))
if out['litrgb_al']: print('AL-lit rgb AL',['%.1f'%S.mean(x[i] for x in out['litrgb_al']) for i in range(3)],'RT',['%.1f'%S.mean(x[i] for x in out['litrgb_rt']) for i in range(3)])
print('fwd RT-AL',' '.join('%d:%+.1f'%(b*32,S.mean(v)) for b,v in sorted(fw.items())))
