# NEXT (s7920)
HYPOTHESIS-ID: g5c-l4-inflight-vi-holds
s7919: owner recipe L1 300 s clean (max gap 148 ms, holds >=250 ms only in the boot/menu route, same as pre-edit s7806).
But s7806 L4 ring (scratch/s7806_gccpatch_L1 sibling scratch/s7806_gccpatch_L4/ring_rL4.txt.zst) has 3 IN-FLIGHT VI-origin holds
273/329/311 ms at 245.5/257.1/259.8 s (presents flowing, guest not swapping).
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks this.
1. Re-run L4 owner recipe (host idle, unlocked): `env R=scratch/s7920_l4 HOLD=300 ALLOW_SLOW=1 ARMS="4:q4L:ROGUESQ_FORCE_SAVE_MISSION=1"`
   with the L4 level selection used by s7806 (copy its ARMS spec from scratch/agent/soak_queue/done/s7806_gccpatch_L4_*.sh) plus the
   cheapest per-frame game-state stamp that is already in the tree (G1B per-VI ring / VI_STAMP=1), then
   `python3 tools/s7919_gap_check.py scratch/s7920_l4/ring_*.txt`.
Hypotheses: H-script (retail cutscene/pause/message freeze: holds recur at the same mission time, guest gfx tasks stop),
H-host (host stall: gfx tasks keep being submitted but present/VI lags; time varies run to run; co-varies with host load),
H-stream (terrain/asset load mid-flight: holds coincide with a cell/stream load burst).
Discriminator: recurrence at the same game time across runs + whether gfx-task submissions continue during the hold.
