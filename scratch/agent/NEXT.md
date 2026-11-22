# NEXT (s7798)
HYPOTHESIS-ID: g6c-standins-dd2-fidelity
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. s7797 queued 13 stand-in re-holds (scratch/agent/soak_queue/s7797_standins_rehold_L{0,2,3,6,7,8,9,11,13,14,16,17,18}.sh,
300 s dd4 STANDINS=1, post-s7790 binary). Fold every verdict that has landed (pass = alive=1/1 crash_arms=0 stall_arms=0, standins_on_line>=1,
spawns>0 on levels with stand-ins). Any crash/stall outranks the unit below: backtrace it and root-cause it (G6c defect).

Unit: post-G6c fidelity at the owner's OTHER draw distance, dd2 (G5 recipe "dd4 (or 2)"). Every post-G6c fidelity arm so far (s7793-s7797) ran at dd4.
Stand-ins fire at dd>1, but at dd2 the far window is smaller, so stand-ins sit nearer the real-object spawn ring, where handoff matters (s7672/s7690).
Level L4 16:9 (155 stand-ins, city towers, the s7628 visual proof level). Screen unlocked, one game:
  check how s7131_arm.zsh sets dd (grep -n 'DRAW_DISTANCE' tools/s7131_arm.zsh); pass ROGUESQ_DRAW_DISTANCE=2 in the env string if it is overridable,
  else add DD=${DD:-4} to the script (a tool change, keep the default 4).
  env RDIR=s7798 zsh tools/s7131_arm.zsh 4 L4d2 "ROGUESQ_DRAW_DISTANCE=2 ROGUESQ_STANDINS=1 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  env JOBS=2 zsh tools/s7141_post.zsh scratch/s7798 L4d2 0,9,369,216 46,322
  python3 tools/s7157_fsum.py scratch/s7798/L4d2.frames.csv scratch/s7798/L4d2_sh2.frames.csv
  zsh tools/s7160_fit_post.zsh scratch/s7798 L4d2 0,10,370,217 docs/owner_sheet_s7798_L4_dd2_standins_fidelity.png
Confirm `[g1c] ... dd=2` / `[standins] on mode=on dd=2.00` in run.log, else the arm is void.
Baseline: s7157/s7158-era L4 16:9 dd4 (grep 'L4 ' near s7157 in PORTING-STATE); expect frac med <=0.010, 0 >0.05.
Hypotheses: H-equal (0 >0.05, at floor), H-handoff (outliers at stand-in<->real swap frames: a stand-in drawn where angrylion... note angrylion
replays our stream, so a handoff gap is in BOTH and the diff can't see it: a handoff defect would show only on the sheet / spawns log, not as
a frac rise), H-dd2 (dd2-specific terrain window difference raises far bands).
Controls: CONTROL painted PASS and shift-2 >0.05 count must fire. Delete .cap/.raw/L4d2r/chunk* after scoring (the s7797 rm glob aborted on zsh nomatch: delete by name).
If H-equal: next ladder rung (item 3c) after folding the re-holds.
