#!/usr/bin/env python3
"""s6934: was a keyed arm in flight or on the pause menu? Reads RAND_TRACE rows from ROGUESQ_XTRACE_MEM=800FA730:0:80137DC0:3,800FA730:0:800C1998:1.
Prints per update_screen bucket: ticks, the pause word values seen (0x800C1998 is HUD+0x258, byte 3 = menu open), and the span of the 3 words at 0x80137DC0 as floats.
A tick row with moving words and pause 0 is flight. usage: g1e_flight_state.py rand.txt [bucket=600]"""
import re, struct, sys
b=int(sys.argv[2]) if len(sys.argv)>2 else 600
M=re.compile(r'm=([0-9a-fA-F]+):([0-9a-fA-F,x]+)')
rows={}
for l in open(sys.argv[1],errors='replace'):
    if ' m=' not in l: continue
    p=l.split(); 
    try: scr=int(p[1],0)
    except: continue
    d={m[1].lower().lstrip('0x'):m[2].split(',') for m in M.finditer(l)}
    r=rows.setdefault(scr//b,dict(n=0,pause=set(),pos=[]))
    r['n']+=1
    for k,v in d.items():
        if k.endswith('c1998'): r['pause'].add(v[0])
        elif k.endswith('137dc0') and len(v)==3:
            r['pos'].append([struct.unpack('>f',bytes.fromhex(x.replace('0x','').zfill(8)))[0] for x in v])
for k in sorted(rows):
    r=rows[k]; s=[max(c)-min(c) for c in zip(*r['pos'])] if r['pos'] else []
    print(k*b,'ticks',r['n'],'pause',sorted(r['pause'])[:4],'span',' '.join('%.2f'%x for x in s))
