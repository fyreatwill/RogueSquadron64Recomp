# s7182: vertical scale/offset fit of AL (painted crop) onto the RT64 presented raw: AL resized to (308,Hk) pasted at row y0.
import sys,csv,importlib.util,statistics as S
sp=importlib.util.spec_from_file_location('f','tools/s7122_fidelity.py');F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F)
from PIL import Image, ImageChops, ImageStat
D,RN,ALD,CSV=sys.argv[1:5]; raw=F.Raw('%s/%s.raw'%(D,RN)); res={}
for r in list(csv.DictReader(open(CSV)))[::6]:
  a=F.load_al('%s/%s/f%s.rgb'%(D,ALD,r['swap']))
  if a is None: continue
  P=raw.img(int(r['pframe'])).convert('L'); a=a.convert('L')
  for Hk in range(227,236):
    A=a.resize((308,Hk),Image.BOX)
    for y0 in (8,9,10):
      q=P.crop((0,y0,308,y0+Hk)); yb=min(Hk,240-y0)-2
      res.setdefault((Hk,y0),[]).append(ImageStat.Stat(ImageChops.difference(q.crop((4,4,304,yb)),A.crop((4,4,304,yb)))).mean[0])
best=sorted((S.mean(v),k) for k,v in res.items())[:5]
print(CSV,'best (mad,(H,y0))',['%.2f %s'%b for b in best],' assumed (233,9): %.2f'%S.mean(res[(233,9)]))
