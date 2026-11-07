#!/usr/bin/env python3
"""s6941: same-run =TOGGLE scorer on the per-second [g1e-split] line (ROGUESQ_G1E_AQ=2): per-task ucode_ms, submit_ms and
rest_ms (= ucode minus RT64 submit, the ucode's own host time), credited by LOG ORDER to the last '[TAG] on=N' flip line;
the first 2 and last 1 seconds of each block are dropped. usage: g1e_split_tog.py LOG TAG [skip_blocks=0]
Prints per-arm medians and ABAB adjacent block-pair diffs (on - off) for each field."""
import re, sys, statistics as st
f, tag = sys.argv[1], sys.argv[2]; skip = int(sys.argv[3]) if len(sys.argv) > 3 else 0
S = re.compile(rb'^\[g1e-split\] .*?tasks=(\d+) ucode_ms=([\d.]+) submit_ms=([\d.]+) rest_ms=([-\d.]+)')
F = re.compile(rb'^\[' + re.escape(tag.encode()) + rb'\] on=(\d) t=')
blocks = []; cur = None
for l in open(f, 'rb'):
    m = F.match(l)
    if m: cur = [int(m[1]), []]; blocks.append(cur); continue
    m = S.match(l)
    if m and cur is not None and int(m[1]) >= 20: cur[1].append(tuple(float(x) for x in m.groups()[1:]))
blocks = blocks[skip:]
bm = []; arm = {0: [], 1: []}
for on, s in blocks:
    s = s[2:-1]
    if len(s) < 3: continue
    arm[on] += s; bm.append((on, [st.median(x[i] for x in s) for i in range(3)]))
names = ('ucode_ms', 'submit_ms', 'rest_ms')
for k in (0, 1):
    v = arm[k]
    if v: print(f'on={k} n={len(v)} ' + ' '.join(f'{nm} med={st.median(x[i] for x in v):.3f}' for i, nm in enumerate(names)))
for i, nm in enumerate(names):
    d = [b[1][i] - a[1][i] if b[0] == 1 else a[1][i] - b[1][i] for a, b in zip(bm, bm[1:]) if a[0] != b[0]]
    if len(d) > 1: print(f'pairs {nm} on-off: n={len(d)} mean={st.mean(d):+.3f} sd={st.stdev(d):.3f} se={st.stdev(d)/len(d)**.5:.3f} lower={sum(x<0 for x in d)}')
