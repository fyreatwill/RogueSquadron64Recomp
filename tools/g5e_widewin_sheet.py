#!/usr/bin/env python3
# s7009 G5e: owner sheet for a =tog lever from a g5b_capture raw (16-byte header <QII mach,w,h + w*h RGB per frame).
# usage: g5e_widewin_sheet.py raw out.png [rows=4] [period_ticks=24e6] [label_off] [label_on]
# Picks `rows` adjacent (off second, next on second) pairs spread over the capture, frame nearest phase 0.5 of each second,
# in flight only (side columns not black). Left column = parity 0 (off), right = parity 1 (on). Half size.
import sys,struct
from PIL import Image,ImageDraw
raw,out=sys.argv[1],sys.argv[2]; R=int(sys.argv[3]) if len(sys.argv)>3 else 4; PER=float(sys.argv[4]) if len(sys.argv)>4 else 24e6
lo=sys.argv[5] if len(sys.argv)>5 else 'off'; lh=sys.argv[6] if len(sys.argv)>6 else 'on'
f=open(raw,'rb'); t,w,h=struct.unpack('<QII',f.read(16)); rec=16+w*h*3; n=f.seek(0,2)//rec
best={}
for i in range(n):
    f.seek(i*rec); t,_,_=struct.unpack('<QII',f.read(16)); s=int(t//PER); ph=abs((t/PER)%1-0.5)
    if s not in best or ph<best[s][0]: best[s]=(ph,i)
def frame(i):
    f.seek(i*rec+16); b=f.read(w*h*3); return Image.frombytes('RGB',(w,h),b)
def inflight(im): return sum(im.getpixel((x,200))[0] for x in (5,10,15))>=30
secs=sorted(best); pairs=[(s,s+1) for s in secs if s%2==0 and s+1 in best]
pairs=[q for q in pairs[1:-1] if inflight(frame(best[q[0]][1])) and inflight(frame(best[q[1]][1]))]; pick=[pairs[int(k*(len(pairs)-1)/max(R-1,1))] for k in range(R)] if len(pairs)>=R else pairs
W2,H2=w//2,h//2; sheet=Image.new('RGB',(2*W2+6,len(pick)*(H2+18)+4),(20,20,20)); d=ImageDraw.Draw(sheet)
for r,(a,b) in enumerate(pick):
    for c,s in enumerate((a,b)):
        im=frame(best[s][1]); y=r*(H2+18)+18
        sheet.paste(im.resize((W2,H2)),(c*(W2+6),y)); d.text((c*(W2+6)+4,y-15),'%s  second %d%s'%((lo,lh)[c],s-secs[0],'' if inflight(im) else ' (not flight)'),fill=(255,255,255))
sheet.save(out); print('sheet',out,len(pick),'pairs')
