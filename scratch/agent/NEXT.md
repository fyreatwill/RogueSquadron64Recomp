# NEXT (s7267): fold s7266_dd6_r88 — does the new auto R=88 hold the dd6 farthest-view line at 60 on L4 21:9?
HYPOTHESIS-ID: widewin-169-tv
State (s7266): auto stack R changed 48 -> 88 in src/main/main.cpp (~12461). At L4 21:9 dd4 R=88 keeps the side gain (hard80 L/R -7.6/-9.6
= STACK=0 control) and win77-97 60/s 12.03 ms. dd6 was qualified only at R=48 (s7257/s7258: R=48 removed 9-14 late dip s).
Results: scratch/s7266 (log_a88/a48/offd, arms.log); the soak prints headroom, flat30, predictor skip, merged, dip runs.
Control: offd must go flat 30 in t=77-97 (else void, re-queue).
Outcomes:
- H-keep6: a88 window <~13 ms, 0 flat runs, beyond-route <55/s s within ~2 of a48 -> dd6 qualified at R=88; then queue a 16:9 dd4 R=88
  cost+edge check (copy scratch/agent/soak_queue/done/s7265_ww_r_*.sh with ROGUESQ_ASPECT=16:9 in W) and close the thread with an owner
  sheet (edge frames WIDEWIN off/on at R=88, from scratch/s7265e captures if kept).
- H-cost6: a88 shows late dips / flat 30 that a48 lacks -> make the auto R per-dd (88 at dd2-5, 48 at dd>=6) in main.cpp, smoke-boot
  both, update OWNER-OPT-INS (dd6 keeps the old cheaper version), queue a dd6 edge check.
- Any crash -> backtrace first.
If the soak has not run (owner active): do not wait; take ladder 3c next open owner-look item (G5h cutscenes background at dd2/dd4).
