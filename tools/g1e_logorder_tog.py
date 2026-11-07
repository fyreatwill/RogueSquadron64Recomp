#!/usr/bin/env python3
"""s6940: same-run =TOGGLE scorer by LOG ORDER. Every [g1b] second is credited to the arm set by the last flip line
('[TAG] on=N') printed before it; the first 2 seconds after a flip and the last 1 before the next are dropped so no
second straddles a flip. Prints per arm: n, tasks/s mean/median, sd_wall median, and an ABAB block-pair mean diff.
usage: g1e_logorder_tog.py LOG TAG [from_t=100]     e.g. g1e_logorder_tog.py run.log g1e-lean 100"""
import re, sys, statistics as st
f, tag = sys.argv[1], sys.argv[2]; t0 = int(sys.argv[3]) if len(sys.argv) > 3 else 100
G = re.compile(rb'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/')
F = re.compile(rb'^\[' + re.escape(tag.encode()) + rb'\] on=(\d)')
blocks = []; cur = None
for l in open(f, 'rb'):
    m = F.match(l)
    if m: cur = [int(m[1]), []]; blocks.append(cur); continue
    m = G.match(l)
    if m and cur is not None and int(m[1]) >= t0: cur[1].append((int(m[3]), float(m[4])))
arm = {0: [], 1: []}; bm = []
for on, s in blocks:
    s = s[2:-1]
    if len(s) < 3: continue
    arm[on] += s; bm.append((on, st.mean(x[0] for x in s), st.median(x[1] for x in s)))
for k in (0, 1):
    v = arm[k]
    if v: print(f'on={k} n={len(v)} tasks/s mean={st.mean(x[0] for x in v):.2f} med={st.median(x[0] for x in v):.1f} sd_wall med={st.median(x[1] for x in v):.2f}')
d = [b[1] - a[1] if b[0] == 1 else a[1] - b[1] for a, b in zip(bm, bm[1:]) if a[0] != b[0]]
if len(d) > 1: print(f'adjacent block pairs tasks/s on-off: n={len(d)} mean={st.mean(d):+.2f} sd={st.stdev(d):.2f} se={st.stdev(d)/len(d)**.5:.2f} positive={sum(x>0 for x in d)}')
w = [b[2] - a[2] if b[0] == 1 else a[2] - b[2] for a, b in zip(bm, bm[1:]) if a[0] != b[0]]
if len(w) > 1: print(f'adjacent block pairs sd_wall ms on-off: n={len(w)} mean={st.mean(w):+.2f} sd={st.stdev(w):.2f} se={st.stdev(w)/len(w)**.5:.2f} negative={sum(x<0 for x in w)}')
