#!/usr/bin/env python3
"""s7268: summarise g5e_edge_score output (edge_<arm>.txt from tools/s7263_widewin_edge_arms.zsh) as WIDEWIN off->on
hard80% deltas per third (L/C/R). fog=0 is the OFF lever half, fog=1 the ON half (TOG_SPLIT=parity).
Usage: python3 tools/s7268_edge_delta.py <outdir> [control_arm] [min_drop]
Prints one line per arm; with control_arm, marks the run VOID unless that arm drops >= min_drop (default 3) on L or R."""
import glob, os, re, sys
d = sys.argv[1]; ctl = sys.argv[2] if len(sys.argv) > 2 else None; md = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
res = {}
for f in sorted(glob.glob(os.path.join(d, 'edge_*.txt'))):
    arm = os.path.basename(f)[5:-4]; h = {}
    for m in re.finditer(r'fog=(\d) third=(\d) cols=\d+ .*?hard80%=([\d.]+)', open(f).read()):
        h[(int(m[1]), int(m[2]))] = float(m[3])
    if len(h) < 6: print(f'{arm}: incomplete ({len(h)}/6 bins)'); continue
    dl = [h[(1, t)] - h[(0, t)] for t in range(3)]; res[arm] = dl
    print(f'{arm}: off L/C/R {h[(0,0)]:.1f}/{h[(0,1)]:.1f}/{h[(0,2)]:.1f} on {h[(1,0)]:.1f}/{h[(1,1)]:.1f}/{h[(1,2)]:.1f}'
          f'  delta L/C/R {dl[0]:+.1f}/{dl[1]:+.1f}/{dl[2]:+.1f}  side gain {-(dl[0]+dl[2]):.1f}')
if ctl:
    c = res.get(ctl)
    ok = c is not None and min(c[0], c[2]) <= -md
    print(f'CONTROL {ctl}: {"PASS" if ok else "VOID"} (needs L or R <= -{md:g})')
    sys.exit(0 if ok else 4)
