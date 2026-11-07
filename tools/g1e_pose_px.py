import sys,os
from PIL import Image, ImageChops
A=os.environ.get('PXA','scratch/s6884/a/')
def L(p):
    i=Image.open(p).convert('RGB'); return i.crop((0,62,i.width,i.height))
def n(a,b):
    d=ImageChops.difference(a,b).convert('RGB'); r,g,bb=d.split(); m=ImageChops.add(ImageChops.add(r,g),bb).point(lambda v:255 if v else 0); return m.histogram()[255]
for x,y in [p.split(':') for p in sys.argv[1:]]:
    o=[]
    for k in range(3):
        px,py=f'{A}{x}/f{k}_1.png',f'{A}{y}/f{k}_1.png'
        if not(os.path.exists(px) and os.path.exists(py)): o.append('miss'); continue
        a,b=L(px),L(py); o.append(n(a,b))
    print(x,y,o,'of',a.width*a.height)
