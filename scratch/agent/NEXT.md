# NEXT (s7800)
HYPOTHESIS-ID: g6c-standins-dd2-handoff
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. 9 s7797 stand-in re-holds still queued (L2,3,6,7,8,9,16,17,18; L0/L11/L13/L14 folded). Fold every verdict
(pass = alive=1/1 crash_arms=0 stall_arms=0 and `s7797 Lx standins_on_line=1 spawns>0` in the log). Any crash/stall outranks the unit.

Unit: dd2 handoff on the heaviest stand-in levels, L12 (131) and L10 (280; cloud level, stand-ins still apply). s7799 closed L4/L1
(H-clean). Same recipe:
  zsh scratch/s7672/run.zsh scratch/s7800 12 odd 2
  zsh scratch/s7672/run.zsh scratch/s7800b 10 odd 2      # L10 needs ROGUESQ_FORCE_PLANET_UNLOCK=0xFF: check the harness sets it, else append to E
  python3 tools/s7672_handoff_score.py <log>; echo $?    # do NOT pipe before reading $? (s7799 misread grep's rc)
Confirm `[standins] on mode=on dd=2.00` + `multiplier 2` in each log, else void.
Hypotheses: H-clean (held blink>1 = 0, far_viol 0, control blinks), H-gap-dense (blinks only where many items hand off at once: the
900-frame cap or the bucket fills), H-none (handoffs 0 -> report si_before_spawn).
If H-clean on both: G6c handoff closed at dd2 on 4 levels; take the next item-3c ladder rung (all owner items wait; pick an
engineering gate from CURRENT-TRUTH item 12 to rerun after the post-s7790 tree, or a new census).
