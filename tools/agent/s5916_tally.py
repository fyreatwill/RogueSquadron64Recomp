#!/usr/bin/env python3
"""Per-30s-window tally of [s5901] class-1 rows (c1f=1) and crossings (best_ratio<=1),
joined to [plpos] el= by log order. Usage: s5916_tally.py run.log"""
import re,sys,collections
el=None;W=collections.OrderedDict();cur=None
for l in open(sys.argv[1],errors='replace'):
    if l.startswith('[plpos]'):
        m=re.search(r'el=([\d.]+).*sx=(\S+) sy=(\S+)',l); el=float(m[1])
        w=int(el//30)*30
        cur=W.setdefault(w,dict(rows=0,c1=0,x=0,sx=set(),sy=set()))
        cur['sx'].add(m[2]);cur['sy'].add(m[3])
    elif l.startswith('[s5901]') and cur is not None:
        m=re.search(r'best_ratio=(\S+) id=(\S+) c1f=(\d)',l)
        cur['rows']+=1
        if m[3]=='1':
            cur['c1']+=1; cur['x']+=float(m[1])<=1
for w,d in W.items(): print(w,d['rows'],'c1f',d['c1'],'cross',d['x'],sorted(d['sx']),sorted(d['sy']))
