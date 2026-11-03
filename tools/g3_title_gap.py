#!/usr/bin/env python3
"""s6808 G3: put port AI feed gaps on a wall clock. Inputs per arm: <p>.ai.txt (ROGUESQ_AI_TRACE, 6th col = VI #) and
<p>.vi.txt (ROGUESQ_VI_WALL: wall s, VI #, width, osViSetMode calls, cumulative host us, run-token holder pri<<16|OSId hex). For every gap >= G3_GAP_MIN VI
between AI buffers: VI span, wall span of the AI gap, wall span of the same VIs, max VI interval inside, osViSetMode calls
and host ms inside, SDL queue bytes before the resuming buffer (0 = audible underrun) and min queue near the gap.
usage: [G3_GAP_MIN=3] g3_title_gap.py PREFIX ...   (PREFIX = scratch/s6808/a)"""
import os, sys
GMIN = int(os.environ.get("G3_GAP_MIN", "3"))
for p in sys.argv[1:]:
    ai = [(float(r[0]), int(r[1]), int(r[5])) for r in (l.split() for l in open(p + ".ai.txt")) if len(r) >= 6]
    vi = {int(r[1]): (float(r[0]), int(r[2]), int(r[3]), int(r[4]), r[5] if len(r) > 5 else '-') for r in (l.split() for l in open(p + ".vi.txt")) if len(r) >= 5}
    walls = sorted(vi.items())
    dts = [walls[i + 1][1][0] - walls[i][1][0] for i in range(len(walls) - 1)]
    dts_s = sorted(dts)
    print(f"{p}: {len(ai)} AI bufs, {len(vi)} VIs, VI interval median {dts_s[len(dts_s)//2]*1000:.1f} ms p99 "
          f"{dts_s[int(len(dts_s)*.99)]*1000:.1f} max {dts_s[-1]*1000:.1f}; qzero total {sum(1 for a in ai if a[1]==0)}")
    for i in range(1, len(ai)):
        g = ai[i][2] - ai[i - 1][2]
        if g < GMIN: continue
        v0, v1 = ai[i - 1][2], ai[i][2]
        if v0 not in vi or v1 not in vi: continue
        mx = max(vi[v + 1][0] - vi[v][0] for v in range(v0, v1) if v + 1 in vi)
        qmin = min(a[1] for a in ai[max(0, i - 4):i + 4])
        print(f"  gap {g:2d} VI {v0}->{v1} w={vi[v1][1]} aiwall {1000*(ai[i][0]-ai[i-1][0]):6.1f} ms  viwall "
              f"{1000*(vi[v1][0]-vi[v0][0]):6.1f} ms  maxVIint {1000*mx:6.1f}  vimode {vi[v1][2]-vi[v0][2]} calls "
              f"{(vi[v1][3]-vi[v0][3])/1000:6.2f} ms  q_resume {ai[i][1]}  qmin+-4 {qmin}  tok {' '.join(vi[v][4] for v in range(v0, v1 + 1) if v in vi)}")
