#!/usr/bin/env python3
"""s7107: contact sheet (PPM; convert with sips) of g5b_capture raw frames around given capture times (clock of the g5b_drops csv).
usage: s7107_sheet.py raw drops.csv out.ppm t1,t2,... [frames per row=6]"""
import sys,struct,os,bisect
raw=sys.argv[1]; csv=sys.argv[2]; out=sys.argv[3]; ts=[float(x) for x in sys.argv[4].split(',')]; K=int(sys.argv[5]) if len(sys.argv)>5 else 6
r0=[l.strip().split(',') for l in open(csv)][1]; cap0=int(r0[6])-float(r0[1])*24e6
f=open(raw,'rb'); t0,w,h=struct.unpack('<QII',f.read(16)); rec=16+w*h*3; n=os.path.getsize(raw)//rec
def mt(i): f.seek(i*rec); return struct.unpack('<Q',f.read(8))[0]
lo,hi=0,n-1
def find(m):
    a,b=0,n-1
    while a<b:
        c=(a+b)//2
        if mt(c)<m: a=c+1
        else: b=c
    return a
rowsimg=[]
for t in ts:
    i=find(cap0+t*24e6); fr=[]
    for k in range(i-K//2,i+K-K//2):
        f.seek(k*rec+16); fr.append(f.read(w*h*3)); print('t=%.3f frame %d mt %.3f'%(t,k,(mt(k)-cap0)/24e6))
    rowsimg.append(fr)
W=w*K; H=h*len(ts); o=open(out,'wb'); o.write(b'P6 %d %d 255\n'%(W,H))
for fr in rowsimg:
    for y in range(h):
        for img in fr: o.write(img[y*w*3:(y+1)*w*3])
