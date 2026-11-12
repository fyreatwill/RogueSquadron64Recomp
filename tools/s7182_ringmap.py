# s7182: zoomed AL | RT64(native, box) | loss map (red = AL lit & RT64 darker by >40) for one swap; plus row/col histogram of loss.
import sys,csv,importlib.util,collections
sp=importlib.util.spec_from_file_location('f','tools/s7122_fidelity.py');F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F)
from PIL import Image
D,RN,ALD,CSV,rect,sw,outp=sys.argv[1:8]; rect=tuple(map(int,rect.split(','))); raw=F.Raw('%s/%s.raw'%(D,RN))
r=[x for x in csv.DictReader(open(CSV)) if x['swap']==sw][0]; a=F.load_al('%s/%s/f%s.rgb'%(D,ALD,sw)).convert('RGB')
p=raw.img(int(r['pframe'])).crop(rect).resize(a.size,Image.BOX)
B=(120,190,410,300); A=a.crop(B); P=p.crop(B); M=Image.new('RGB',A.size); rows=collections.Counter(); cols=collections.Counter(); gain=0
for y in range(A.size[1]):
  for x in range(A.size[0]):
    la=sum(A.getpixel((x,y)))/3; lp=sum(P.getpixel((x,y)))/3; g=int(la/2)
    if la-lp>40: M.putpixel((x,y),(255,0,0)); rows[y+B[1]]+=1; cols[(x+B[0])//10*10]+=1
    elif lp-la>40: M.putpixel((x,y),(0,255,0)); gain+=1
    else: M.putpixel((x,y),(g,g,g))
W,H=A.size; S=Image.new('RGB',(W*3,H)); S.paste(A,(0,0)); S.paste(P,(W,0)); S.paste(M,(2*W,0)); S.resize((W*9,H*3),Image.NEAREST).save(outp)
print('swap',sw,'loss px',sum(rows.values()),'gain px',gain); print('loss rows',sorted(rows.items())[:40]); print('loss cols',sorted(cols.items()))
