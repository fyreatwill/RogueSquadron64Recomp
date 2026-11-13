#!/usr/bin/env python3
# s7039: frames G before/after listed tog3 edges, labelled by cull phase (0 off, 1 stack R88 R2 K0.6, 2 ungated R0). usage: sheet.py RAW OUT G frame [frame...]
import struct,sys
from PIL import Image,ImageDraw,ImageChops
raw,out,G=sys.argv[1],sys.argv[2],int(sys.argv[3]); fr_=list(map(int,sys.argv[4:]))
f=open(raw,'rb'); t0,w,h=struct.unpack('<QII',f.read(16)); rec=16+w*h*3
def fr(i):
    f.seek(i*rec); t=struct.unpack('<Q',f.read(8))[0]; f.seek(i*rec+16); return t,Image.frombytes('RGB',(w,h),f.read(w*h*3))
L=['off','stack R88','R1+R0cull ctl']; tw=w*2; th=h*2; im=Image.new('RGB',(tw*3,(th+14)*len(fr_)),(20,20,20)); d=ImageDraw.Draw(im)
for k,i in enumerate(fr_):
    (ta,a),(tb,b)=fr(i-G),fr(i+G); Y=k*(th+14)
    for x,(t,g) in enumerate(((ta,a),(tb,b))):
        im.paste(g.resize((tw,th)),(x*tw,Y+14)); d.text((x*tw+3,Y+1),'%s t=%.2f'%(L[(t//24000000)%3],(t-t0)/24e6),fill=(255,255,0))
    df=ImageChops.difference(a,b).point(lambda v:min(255,v*4)); im.paste(df.resize((tw,th)),(2*tw,Y+14)); d.text((2*tw+3,Y+1),'|diff| x4',fill=(255,255,0))
im.save(out,quality=85)
