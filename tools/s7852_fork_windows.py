#!/usr/bin/env python3
"""s7852: list EVERY rand fork window of a det pair, not just the first (s7845_rng_tick_cmp.py stops at the first).
A window = a maximal run of ticks whose seed or rand-caller list differs, retail vs port (tick k = k-th 0x800FA730).
Per window: ticks, VI at window start on each side (from the trace's VI column), the caller multiset delta, and whether the
seed realigns after it (realign + equal caller multiset over the window = a pure tick-PHASE shift of the same calls).
--control: drops one rand call from port tick 1 and must report a window at tick 1 (positive control).
usage: s7852_fork_windows.py RETAIL_ORACLE_LOG PORT_RAND_TXT [--control]"""
import sys, collections
src = open(__file__.replace('s7852_fork_windows.py', 's7845_rng_tick_cmp.py')).read()
exec(src[:src.index('R, rpre = load(')])  # reuse load() + PORT_MARKS verbatim
R, _ = load(sys.argv[1], True); P, _ = load(sys.argv[2], False)
if '--control' in sys.argv: P[1]['calls'] = P[1]['calls'][1:]
n = min(len(R), len(P)); bad = [k for k in range(n) if R[k]['seed'] != P[k]['seed'] or R[k]['calls'] != P[k]['calls']]
W = []
for k in bad:
    if W and k == W[-1][-1] + 1: W[-1].append(k)
    else: W.append([k])
print(f'ticks retail {len(R)} port {len(P)} compared {n}; differing ticks {len(bad)} in {len(W)} window(s)')
for w in W[:40]:
    a, b = w[0], w[-1]
    rc = collections.Counter(c for k in w for c in R[k]['calls']); pc = collections.Counter(c for k in w for c in P[k]['calls'])
    d = {('%08x' % c): rc[c] - pc[c] for c in set(rc) | set(pc) if rc[c] != pc[c]}
    re_ = b + 1 < n and R[b+1]['seed'] == P[b+1]['seed']
    print(f' ticks {a}-{b} ({len(w)}) vi r={R[a]["vi"]} p={P[a]["vi"]} | caller delta r-p {d or "none"} | realign@{b+1}={re_}'
          f' | {"PHASE-SHIFT" if re_ and not d else "FORK"}')
