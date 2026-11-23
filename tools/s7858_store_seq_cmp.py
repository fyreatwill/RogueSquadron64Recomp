#!/usr/bin/env python3
"""s7858: compare the per-tick store sequence to watched words, retail oracle vs port.
retail: oracle.log with --watch-write A:B --hit-vi-window --hit-cap big: '[hit] w addr=.. pc=.. vi=.. val=..' (val = word BEFORE
the store); the tick is the count of preceding '[xtrace] .. pc=800fa730' rows (the s7854 record ordinal: row k = state at tick k start,
so stores stamped k produce row k).  port: run.log '[swatch-pt] .. pc=.. phys=.. pre=w0..w3 tick=k' (ROGUESQ_STORE_WATCH_PTS, s7858
tick stamp = count of 800FA730 marks so far).  The value each store wrote is recovered from the next store's pre, or the next record row.
usage: s7858_store_seq_cmp.py oracle.log port_run.log port_rand.txt ADDR[,ADDR..] [--ticks A:B]"""
import re, sys
sys.path.insert(0, 'tools')
from rs64_zopen import zopen
orl, prl, prt, addrs = sys.argv[1:5]
A = [int(x, 16) & 0x1FFFFFFF for x in addrs.split(',')]
t0, t1 = (int(x) for x in sys.argv[sys.argv.index('--ticks') + 1].split(':')) if '--ticks' in sys.argv else (0, 10**9)
seg = re.compile(r'm=([0-9a-f]{8}):([0-9a-f,]+)')
def rec_rows(lines, retail):
    out = []
    for l in lines:
        if retail and not (l.startswith('[xtrace] ') and ' pc=800fa730' in l): continue
        if not retail:
            f = l.split(None, 3)
            if len(f) < 3 or f[2] != '800fa730': continue
        w = {}
        for a, vs in seg.findall(l):
            a = int(a, 16) & 0x1FFFFFFF
            for k, v in enumerate(vs.split(',')): w[a + 4 * k] = int(v, 16)
        out.append(w)
    return out
R = {a: [] for a in A}; tick = 0; rrows = []
for l in zopen(orl):
    if l.startswith('[xtrace] ') and ' pc=800fa730' in l:
        rrows.append(l); tick += 1; continue
    if l.startswith('[hit] w '):
        m = re.search(r'addr=0x([0-9a-f]+) pc=0x([0-9a-f]+).* vi=(\d+) val=0x([0-9a-f]+)', l)
        if m and int(m[1], 16) in R: R[int(m[1], 16)].append((tick - 1 + 1, int(m[2], 16), int(m[4], 16)))
RR = rec_rows(rrows, True)
P = {a: [] for a in A}
for l in zopen(prl):
    if l.startswith('[swatch-pt] '):
        m = re.search(r'pc=([0-9A-F]+) phys=([0-9A-F]+) len=(\d+) pt=([0-9A-F]+) pre=(\S+) (\S+) (\S+) (\S+) tick=(\d+)', l)
        if not m: continue
        ph, n, pt = int(m[2], 16), int(m[3]), int(m[4], 16)
        for a in A:
            if ph <= a < ph + max(n, 4) and pt <= a < pt + 16:
                P[a].append((int(m[9]), int(m[1], 16), int(m[5 + (a - pt) // 4], 16)))
PR = rec_rows(zopen(prt), False)
def post(seq, i, rows, a):  # value written by store i: next store's pre, else next record row (row of tick+0 if later tick)
    if i + 1 < len(seq): return seq[i + 1][2]
    t = seq[i][0]; return rows[t].get(a) if t < len(rows) else None
for a in A:
    rs = [(t, pc, pre, post(R[a], i, RR, a)) for i, (t, pc, pre) in enumerate(R[a])]
    ps = [(t, pc, pre, post(P[a], i, PR, a)) for i, (t, pc, pre) in enumerate(P[a])]
    rs = [x for x in rs if t0 <= x[0] <= t1]; ps = [x for x in ps if t0 <= x[0] <= t1]
    print(f'== {a:06X}: retail stores {len(rs)} (ticks {rs[0][0] if rs else "-"}-{rs[-1][0] if rs else "-"}), port stores {len(ps)}')
    pcs = lambda s: sorted(set(x[1] for x in s))
    print('  pcs retail', ' '.join(f'{p:08x}' for p in pcs(rs)), '| port', ' '.join(f'{p:08x}' for p in pcs(ps)))
    pi = {}
    for x in ps: pi.setdefault(x[0], []).append(x)
    ri = {}
    for x in rs: ri.setdefault(x[0], []).append(x)
    shown = 0
    for t in sorted(set(ri) & set(pi)):
        r, p = ri[t], pi[t]
        same = [(y[1], y[3]) for y in r] == [(y[1], y[3]) for y in p]
        if not same and shown < 12:
            shown += 1
            print(f'  t{t} DIFF retail ' + ' '.join(f'{y[1]:08x}:{y[2]:08x}->{(y[3] or 0):08x}' for y in r))
            print(f'  {"":>{len(str(t))+1}}      port   ' + ' '.join(f'{y[1]:08x}:{y[2]:08x}->{(y[3] or 0):08x}' for y in p))
    nd = sum(1 for t in set(ri) & set(pi) if [(y[1], y[3]) for y in ri[t]] != [(y[1], y[3]) for y in pi[t]])
    print(f'  common ticks {len(set(ri) & set(pi))}, differing {nd}, retail-only ticks {len(set(ri)-set(pi))}, port-only {len(set(pi)-set(ri))}')
