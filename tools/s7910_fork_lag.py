#!/usr/bin/env python3
"""s7910 G3: content lag of a det pair across a fork, by per-frame triangle count (the s7868 frame signatures stop
matching after a fork when the two sides sample a time-keyed animation at different sub-frame phases, so exact
signatures cannot pair them; triangle count still tracks scene content).

For each window [lo,hi) of PORT frame indices, finds the retail-minus-port lag L (searched over --lags a:b) minimising
sum |ntri(port i) - ntri(retail i-L)|, and prints the lag at several ntri threshold crossings after --fork.
Interpretation (s7909/s7910): frame-count keyed content keeps the pre-fork lag; content keyed on elapsed VI / real time
shifts by (stall VI difference)/2 frames (m11 island B: 71 -> 71 + 57/2 = 99.5).
Control (iron rule 1, same run): the --ctl window (default = the 160 frames before --fork) must give lag --ctl-lag
(default 71) with error 0 (frame-exact), rc 3 otherwise.
Evidence pair (s7910, kept captures): scratch/s7895/m11k/r1/retail.bin + scratch/s7905/s7905_island_b_rep3/p1.bin
(replica scratch/s7905/m11C/p1.bin): control lag 71 err 0, post-fork lag 99 in both windows and at all thresholds.
usage: s7910_fork_lag.py RETAIL.bin[.zst] PORT.bin[.zst] [--fork 2559] [--end 2960] [--ctl-lag 71] [--lags 40:140]
"""
import sys, os, importlib.util, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rs64_zopen

a = sys.argv[1:]
def opt(k, d):
    if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    return d
FORK, END, CL = int(opt('--fork', 2559)), int(opt('--end', 2960)), int(opt('--ctl-lag', 71))
L0, L1 = map(int, opt('--lags', '40:140').split(':'))
if len(a) != 2: print(__doc__); sys.exit(2)
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
tmp = tempfile.mkdtemp(prefix='s7910_')
def ntris(p, retail):
    return [sum(v for k, v in c.items() if k[0] == 'tri') for c, _ in m.frames(rs64_zopen.materialize(p, tmp), retail)]
rt, pt = ntris(a[0], True), ntris(a[1], False)

def best(lo, hi):
    lo = max(lo, L1); hi = min(hi, len(pt), len(rt) + L0)
    err = lambda L: sum(abs(pt[i] - rt[i - L]) for i in range(lo, hi))
    b = min(range(L0, L1 + 1), key=err); return b, err(b), lo, hi

cl, ce, _, _ = best(FORK - 160, FORK)
print(f'control window [{FORK - 160},{FORK}): lag {cl} err {ce} (want lag {CL} err 0)')
for lo, hi in ((FORK, FORK + 140), (FORK + 140, END)):
    b, e, lo, hi = best(lo, hi)
    print(f'window [{lo},{hi}): best lag {b} err {e}  (err at pre-fork lag {CL}: {sum(abs(pt[i] - rt[i - CL]) for i in range(lo, hi))})')
for th in (420, 600, 740, 1000):
    p = next((i for i in range(FORK, min(END + 40, len(pt))) if pt[i] > th), None)
    r = next((i for i in range(FORK - CL - 40, min(END, len(rt))) if rt[i] > th), None)
    print(f'ntri>{th}: port {p} retail {r} lag {p - r if p is not None and r is not None else "na"}')
ok = cl == CL and ce == 0
print('control:', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 3)
