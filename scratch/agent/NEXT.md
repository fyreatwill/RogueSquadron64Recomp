# NEXT: FPS60 near-wall flicker: which terrain cell paints the wall, and are its triangles present / with what z on the dropped frame
HYPOTHESIS-ID: fps60-wall-painter
Context (s7106): the ucode turns the 9 near-eye cells' TRI_GENs into screen-covering triangles on the event swaps of 8/10 episodes
(src/rsp/s7106_rsptri.cpp; control ucode parse == bridge tris on 8505/8505 swaps). H-clip refuted as the general cause.
Unit (one build, one run):
 1. Widen the key publish to all 49 cells (tools/apply_s7106_rsptri.py: drop the ring<=1 test, j = i, arrays [49]; s7106_rsptri.cpp
    near[] -> 49, keep the per-swap rt line compact: only cells with seen>0).
 2. In s7106_rsptri.cpp also write, per triangle parsed for a matched cell, a compact record to a binary side file
    (ROGUESQ_S7106_TRIS=<file>): swap, cell index, op, the 5 edge vertices (as G5B_TRIS), the top z (op&1) and shade alpha.
    Or simpler: run with ROGUESQ_G5B_TRIS as well and store, per swap, the ordinal range of each matched cell's tris (tall counter at
    the start/end of the command), since tall == bridge order (s7106 control).
 3. Same arm: scratch/s7099/arm.zsh 6 4 s7107a "ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600 ROGUESQ_G3C_LOG=1
    ROGUESQ_S7101_CHASE=$PWD/scratch/s7107/push_a.txt ROGUESQ_S7104_CELL=1 ROGUESQ_S7105_EMIT=1 ROGUESQ_S7106_RSPTRI=$PWD/scratch/s7107/rt_a.txt
    ROGUESQ_G5B_TRIS=$PWD/scratch/s7107/tris_a.bin" 120 240 ; split via tools/s7099_wall_split.py raw csv run.log.
 4. Offline: for each episode, the drop region (g5b_drops csv) on the dropped frame vs 2 frames before: last painter per screen cell
    (tools/g5b_cover_map.py / g5b_point_stack.py) labelled with the source cell.
Hypotheses:
 H-elsewhere  the wall region's painter on clean frames is a ring>=2 cell or a non-TRI_GEN draw, and that source's tris are absent
              on the dropped frame -> follow that source (CPU list / ucode count for it)
 H-rdp        the painter's triangles are present on the dropped frame but are overdrawn/lose z (sky, a later draw) or carry a z/alpha
              change -> z/blend path (compare z of the same cell across the event)
 H-frame      no difference in the stream at swap granularity -> the loss is inside a swap (presented frame vs swap pairing at FPS60)
Positive control: the same painter map on a clean frame must name the eye/near cells for the ground under the craft.
s7106 leftovers: t=211.2 (eye cell lod-0 05050000 gives 0-1 tris throughout) and t=158.6 (frame total 7623 -> 2952 into the event).
Default stays retail.
