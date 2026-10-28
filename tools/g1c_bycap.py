#!/usr/bin/env python3
"""s6542: bin g1b sd_wall/tasks and capalt taken/rejected by the cap in force (last [capalt] line before each [g1b] line). Usage: g1c_bycap.py run.log"""
import re,sys,statistics as st,collections
cur=None; sd=collections.defaultdict(list); tk=collections.defaultdict(list); taken=collections.defaultdict(list); rej=collections.defaultdict(list)
for l in open(sys.argv[1],errors='replace'):
    m=re.match(r'\[capalt\] swap=(\d+) cap=(-?\d+) taken=(\d+) rejected=(\d+)',l)
    if m: cur=int(m.group(2)); taken[cur].append(int(m.group(3))); rej[cur].append(int(m.group(4))); continue
    m=re.search(r'\[g1b\][^\n]*sd_wall=([\d.]+)/',l)
    if m and cur is not None:
        sd[cur].append(float(m.group(1)))
        t=re.search(r'tasks=(\d+)',l)
        if t: tk[cur].append(int(t.group(1)))
for c in sorted(taken):
    f=lambda a: f'{st.mean(a):.1f}' if a else 'na'
    print(f'cap={c:>4} swaps={len(taken[c])} taken_mean={f(taken[c])} rej_mean={f(rej[c])} | g1b n={len(sd[c])} sd_wall_mean={f(sd[c])} p50={sorted(sd[c])[len(sd[c])//2] if sd[c] else "na"} tasks/s={f(tk[c])}')
