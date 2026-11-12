# s7182: interior vs edge split. Interior lit = AL pixel lit (>224) with all 8 neighbours lit; edge = AL lit/bright pixel within 1 px
# of an AL luma step >60. Reports RT64-AL per class and the share of loss pixels (AL-RT>40) that are edge pixels.
import sys,csv,importlib.util,statistics as S
sp=importlib.util.spec_from_file_location('f','tools/s7122_fidelity.py');F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F)
from PIL import Image
D,RN,ALD,CSV,rect=sys.argv[1:6]; lo,hi=map(int,sys.argv[6].split(',')); rect=tuple(map(int,rect.split(','))); raw=F.Raw('%s/%s.raw'%(D,RN))
B=(141,218,391,284); di=[]; de=[]; ia=[]; ip=[]; loss=0; loss_edge=0; n=0
for r in list(csv.DictReader(open(CSV)))[::2]:
  s=int(r['swap'])
  if not (lo<=s<=hi) or int(r['pframe'])<=0: continue
  a=F.load_al('%s/%s/f%s.rgb'%(D,ALD,s))
  if a is None or a.size!=(512,339): continue
  n+=1; p=raw.img(int(r['pframe'])).crop(rect).resize(a.size,Image.BOX); A=a.convert('L').load(); P=p.convert('L').load(); AR=a.load(); PR=p.load()
  for y in range(B[1],B[3]):
    for x in range(B[0],B[2]):
      nb=[A[x+i,y+j] for i in (-1,0,1) for j in (-1,0,1)]; edge=max(nb)-min(nb)>60; d=P[x,y]-A[x,y]
      if A[x,y]>224 and min(nb)>224: di.append(d); ia.append(AR[x,y]); ip.append(PR[x,y])
      elif edge: de.append(d)
      if d<-40: loss+=1; loss_edge+=edge
print('swaps',lo,hi,'n',n,'| interior lit px %d RT-AL mean %+.2f median %+d | AL rgb %s RT rgb %s'%(len(di),S.mean(di),S.median(di),[round(S.mean(c[i] for c in ia),1) for i in range(3)],[round(S.mean(c[i] for c in ip),1) for i in range(3)]))
print('  edge px %d RT-AL mean %+.2f | loss px (AL-RT>40) %d, of which on an AL edge %.1f%%'%(len(de),S.mean(de),loss,100*loss_edge/max(loss,1)))
