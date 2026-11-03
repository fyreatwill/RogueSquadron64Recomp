#!/usr/bin/env python3
"""s6818: hp lost by the player in the lvl14 15.0-16.5 s terrain-scrape window per trace (800fa730 rows with m=80137db0).
usage: g3_scrape_damage.py HZ TRACE..."""
import struct,sys
fl=lambda w: struct.unpack('>f',struct.pack('>I',w))[0]
hz=float(sys.argv[1])
for p in sys.argv[2:]:
    k=0;prev=None;drops=[]
    for ln in open(p):
        f=ln.split()
        if len(f)<5 or f[2]!='800fa730': continue
        m={x[2:].split(':')[0]:x[2:].split(':')[1].split(',') for x in f[4:] if x.startswith('m=')}
        hp=fl(int(m['80137db0'][0xCC//4],16))
        t=k/hz
        if prev is not None and hp<prev-0.5 and 15.0<t<16.5: drops.append((round(t,3),round(prev-hp,1)))
        prev=hp;k+=1
        if t>16.5: break
    print(p.split('/')[-2] if 0 else p.split('/')[-1], 'scrape dmg',sum(d for _,d in drops),drops)
