#!/usr/bin/env python3
# s7154 owner sheet: OPTIONS / PASSCODES / MISSION FAILED / results at 16:9 (owner recipe), RT64 presented | angrylion replay (NOPREFILL:
# its pillars show the stale RAM real hardware would show; RT64 presents black). usage: s7154_sheet.py dir out.png
import sys,csv,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import s7122_fidelity as F
from PIL import Image, ImageDraw
D,O=sys.argv[1:3]; R=(0,9,369,216); W,H=369,207
pick=[('O1','opt',1150,1800,'OPTIONS'),('O1','pc',2050,2700,'PASSCODES'),('D1','fail',6150,6390,'MISSION FAILED'),('D1','res',6400,6850,'mission results')]
sh=Image.new('RGB',(2*W+6,len(pick)*(H+14)),(30,30,30)); d=ImageDraw.Draw(sh)
for i,(N,_,a,b,t) in enumerate(pick):
    rows=[r for r in csv.DictReader(open('%s/%sJ.csv'%(D,N))) if a<=int(r['swap'])<b]; r=rows[len(rows)*2//3]; y=i*(H+14)
    sh.paste(F.Raw('%s/%s.raw'%(D,N)).img(int(r['pframe'])).crop(R),(0,y+14)); al=F.load_al('%s/%sn/f%s.rgb'%(D,N,r['swap']))
    if al: sh.paste(al.resize((W,H)),(W+6,y+14))
    d.text((2,y+1),'%s  16:9 FPS60 dd4  RT64 (left) | angrylion (right, stale-RAM pillars)  swap %s'%(t,r['swap']),fill=(255,255,0))
sh.save(O); print(O,sh.size)
