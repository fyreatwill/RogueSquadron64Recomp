#!/usr/bin/env python3
"""s7268: summarise g5e_edge_score output (edge_<arm>.txt from tools/s7263_widewin_edge_arms.zsh) as WIDEWIN off->on
hard80% deltas per third (L/C/R). fog=0 is the OFF lever half, fog=1 the ON half (TOG_SPLIT=parity).
Usage: python3 tools/s7268_edge_delta.py <outdir> [control_arm] [min_drop] [ref_arm:min_gain ...]
Prints one line per arm; with control_arm, marks the run VOID unless that arm drops >= min_drop (default 3) on L or R.
s7269: each ref_arm:min_gain (e.g. s0:6) prints MEASURABLE/UNMEASURABLE: the reference arm's side gain (-(dL+dR)) must reach
min_gain, else comparisons against it are within the run's noise (s7268_169_split: 16:9 STACK=0 gave -0.1, s7264 8.9)."""
import glob, os, re, sys
d = sys.argv[1]; ctl = sys.argv[2] if len(sys.argv) > 2 else None; md = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
refs = [a.split(':') for a in sys.argv[4:]]
res = {}
for f in sorted(glob.glob(os.path.join(d, 'edge_*.txt'))):
    arm = os.path.basename(f)[5:-4]; h = {}
    for m in re.finditer(r'fog=(\d) third=(\d) cols=\d+ .*?hard80%=([\d.]+)', open(f).read()):
        h[(int(m[1]), int(m[2]))] = float(m[3])
    if len(h) < 6: print(f'{arm}: incomplete ({len(h)}/6 bins)'); continue
    dl = [h[(1, t)] - h[(0, t)] for t in range(3)]; res[arm] = dl
    print(f'{arm}: off L/C/R {h[(0,0)]:.1f}/{h[(0,1)]:.1f}/{h[(0,2)]:.1f} on {h[(1,0)]:.1f}/{h[(1,1)]:.1f}/{h[(1,2)]:.1f}'
          f'  delta L/C/R {dl[0]:+.1f}/{dl[1]:+.1f}/{dl[2]:+.1f}  side gain {-(dl[0]+dl[2]):.1f}')
rc = 0
for ra, mg in refs:
    r = res.get(ra); g = None if r is None else -(r[0] + r[2])
    ok = g is not None and g >= float(mg)
    print(f'REF {ra}: {"MEASURABLE" if ok else "UNMEASURABLE"} (side gain {g if g is None else round(g, 1)}, needs >= {mg})')
    rc = rc if ok else 5
if ctl:
    c = res.get(ctl)
    ok = c is not None and min(c[0], c[2]) <= -md
    print(f'CONTROL {ctl}: {"PASS" if ok else "VOID"} (needs L or R <= -{md:g})')
    sys.exit(rc if ok else 4)
sys.exit(rc)
