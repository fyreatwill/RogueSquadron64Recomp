# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: real 16:9 per-level G1e game-fps sweep (s6990 flew level 1 every time), now with the s6992 PTRMASK fix in the binary
HYPOTHESIS-ID: g1e-game-fps
State: L15 21:9 crash fixed s6992 (tools/apply_s6993_ptrmask.py, ROGUESQ_PTRMASK default on). 21:9 per-level done s6991 (58.2-60, L15 not measured
because it crashed). Missing: 16:9 per level, and the L15 21:9 fps number.
Hypotheses:
- H-60w: every level holds ~60 shown/s at 16:9 (21:9 did on 18/19) -> G1e lever (1) closes for both owner aspects.
- H-level-cost: some levels (0/4/6/7/16/17 were 58-59.6 at 21:9) drop more at 16:9 or less; dense-scene cost, not aspect.
- H-ptrmask-side: the s6992 mask change shifts palettes or memory on other levels (16:9 fed 6 spill pointers before the fix): look for any crash/oob.
Unit: copy scratch/s6991/drive.sh to scratch/s6993/drive169.sh with R=scratch/s6993s, ASPECT=16:9, level list 0..18 plus C30, HOLD=240; also run
L15 at 21:9 once (arm L15w). Score with tools/g1e_level_fps.py (check `cur` == level on every arm). Keep ROGUESQ_MATWATCH off (store diag slows).
Expected: shown/s per level; any level < 58 gets its sd_wall p50/p90 compared with its 21:9 row.
Host: harness exits 2 on human input (idle < 120 s); check `ioreg -c IOHIDSystem` idle first; if busy, queue arms as soaks.
