# NEXT (s7260): fold s7259_l12_dd6_stack — does the dd6 auto WIDEWIN stack lift level 12's 21:9 limit?
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7259): dd6 auto stack engages in mission on the default path (9.99 ms L4 window, 0 late dips; STACK=0 13.40 ms + 10 dip s; control PASS)
and removes no visible side terrain at dd6 (same-run tog, holes control PASS 136/142, flip +0.0058 +- 0.0050; seams +1.2 vs A/A -2.8): H-clean.
Open: L12 at 21:9 dd6 runs 54-55/s whatever the cap (s7049/s7055, OWNER-OPT-INS). Queue: scratch/agent/soak_queue/s7259_l12_dd6_stack.sh
(SOAK_NEEDS_IDLE=180; arms auto / off=STACK=0 / offd=off+DUTY1.4 control; results in scratch/s7259q).
1. Fold: control offd must show clearly more <55/s seconds than off (else the soak cannot discriminate: re-run).
   H-ww (L12's limit is WIDEWIN cost): auto <55/s seconds far below off, p50 sd_wall down ~3-4 ms -> update OWNER-OPT-INS level-12 note (limit lifted).
   H-other (limit is not WIDEWIN cost: dd6 radius / offmap cull / CPU side): auto ~= off -> split with G1CF rsp vs cpu fields (tools/s7231_cost_decomp.py) in one
   follow-up run, arms auto vs auto+ROGUESQ_DD_WIDEWIN=0.
   Check log_*.txt has the LEVEL line (no "LEVEL MISMATCH" in arms.log) and [s7258] in auto only.
2. If the soak did not run (owner active): next G-ladder unit is extending the auto stack to WIDEWIN at dd2-dd5 (s7247 image check dd4 clean, s7248 dd4 60/s
   fixed-on): code change in main.cpp rs64_g1c_apply_dd_policy outside the dd>=6 branch, startup check [s7258] at dd4, queue auto/off/offd at dd4 L4.
Capture lesson: any g5b_capture arm must keep the game frontmost (scratch/s7259/arm.zsh re-fronts every 10 s); tools/s7247_tog_pop.py now VOIDs starved captures.
