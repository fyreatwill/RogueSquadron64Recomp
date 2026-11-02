#!/usr/bin/env python3
# G3 (s6779): print each VI width change (t, width, origin) from an rs64_oracle --vi-poll log. usage: width_timeline.py ORACLE_LOG
import re,sys
prev=None
for l in open(sys.argv[1],errors='replace'):
    m=re.search(r'\[vi-poll\] t=\s*([\d.]+)s WIDTH \d+ [-=]> (\d+) origin=0x([0-9a-f]+)',l)
    if not m: continue
    k=m.group(2)
    if k!=prev: print(m.group(1),k,m.group(3))
    prev=k
