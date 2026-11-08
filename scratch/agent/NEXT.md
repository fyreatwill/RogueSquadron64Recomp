# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.
# NOTE: CURRENT-TRUTH is 60.4 KB -> Step 0 makes the next iteration MAINTENANCE. Do that first; this unit follows it.

# NEXT: G1e residual - why dense levels 16 (56.3 shown/s) / 7 (57.2) / 17 (58.5) miss game frames at 16:9 dd4
HYPOTHESIS-ID: g1e-dense-level-cost
Data: scratch/s6993s/log_L16.txt, ring_L16.txt (owner recipe, 240 s), same for L7/L17; 60-fps levels (L10, L15) as controls.
Hypotheses:
- H-rsp: gfx RSP task host-ms (sd_wall) exceeds the 16.7 ms budget on missed frames (sd90 is only 8.6 on L16, so check the per-frame tail at the misses).
- H-guest: the game thread's own sim/CPU time per frame (recompiled code) overruns on dense scenes; RSP is idle-waiting.
- H-dd: the miss comes from dd4's extra terrain (dd1 same level should hold 60): one arm L16 dd1 vs dd4.
Unit: OFFLINE first: join ring_L16 misses with [g1b] per-second sd_wall/us_wall/guest-cpu in log_L16 (python pass) and compare
with L10. If inconclusive, run one 2-arm A/B (L16 dd4 vs dd1, same harness: scratch/s6993/drive169.sh pattern, HOLD=240).
Expected: misses co-vary with sd_wall -> H-rsp; with guest cpu and not sd_wall -> H-guest; vanish at dd1 -> H-dd.
Passive: boot freeze self-sample is armed (ROGUESQ_STALL_SAMPLE_DIR); on any [stall-dump] run tools/sample_game_threads.py on the file.
