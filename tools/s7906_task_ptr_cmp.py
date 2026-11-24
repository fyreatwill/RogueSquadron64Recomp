#!/usr/bin/env python3
"""s7906: compare the per-phase gfx task data-pointer stream of two (or more) port run.logs.

usage: tools/s7906_task_ptr_cmp.py [--phase 6] REF_run.log OTHER_run.log [...]
For each run: phase = count of [phase] vi_width changes; per [lle task] in that phase it records
(game frames done so far in the phase from [dt7835] fr lines, data=). Prints the frame-index lag
histogram (task/frame interleave) and, against REF, the indices where data= differs and whether the
lag pattern differs. s7905/s7906: island B soaks had identical interleave to the exact control but
resubmitted the previous odd-stream DL at crawl task 2665 (one stream one task late to ~2885)."""
import sys, collections, argparse
ap = argparse.ArgumentParser(); ap.add_argument('--phase', type=int, default=6); ap.add_argument('logs', nargs='+')
a = ap.parse_args()
R = {}
for p in a.logs:
    ph = 0; w = None; fr = 0; out = []
    for l in open(p, errors='replace'):
        if l.startswith('[phase] vi_width='):
            nw = int(l.split('=')[1].split()[0])
            if nw != w: ph += 1; w = nw; fr = 0
        elif l.startswith('[dt7835] fr'): fr += 1
        elif l.startswith('[lle task]') and ph == a.phase:
            out.append((fr, l.split('data=')[1].split()[0]))
    R[p] = out
    lag = collections.Counter(f - i for i, (f, d) in enumerate(out))
    print(f'{p}: tasks {len(out)} lag hist {sorted(lag.items())[:8]}')
ref = R[a.logs[0]]
for p in a.logs[1:]:
    b = R[p]
    dd = [i for i, (x, y) in enumerate(zip(ref, b)) if x[1] != y[1]]
    lg = [i for i, (x, y) in enumerate(zip(ref, b)) if x[0] - y[0] != ref[0][0] - b[0][0]]
    print(f'vs {p}: data-ptr diffs {len(dd)} first {dd[:6]} last {dd[-3:]} | interleave diffs {len(lg)} first {lg[:4]}')
    if dd:
        i = dd[0]
        for k in range(max(0, i - 2), min(len(b), i + 4)): print(f'   task {k}: ref {ref[k][1]} other {b[k][1]}')
