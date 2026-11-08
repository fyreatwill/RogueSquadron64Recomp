# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: does ROGUESQ_VI_LOCK prevent 21:9 level entries, and does it help 16:9?
HYPOTHESIS-ID: g1e-submit-phase-lock
s6968: opt-in ROGUESQ_VI_LOCK=1 (VI grid servoed so RT64's W submit sits 10 ms after the display vsync) cut 21:9 dd4 lat p50 ~31 -> 23.4
same run 3/3 (tools/g1e_vi_lock_ab.py). Untested: level prevention (before-blocks were 35 s with no level) and 16:9.
0. Fold soaks s6968_vilock_169_l1/l2 (SOAK-RESULTS.md, scratch/s6968q): after-block W p50 ~10 = control; lat p50 before vs after.
1. ONE batch, lvl1 21:9 dd4 FPS60, NO drain, RT default, HOLD 260, tools/g1e_owner_quiet_arms.zsh (R=scratch/s6969), 4 arms run
   sequentially: two with ROGUESQ_VI_LOCK=1 from boot, two without. Score per arm with tools/g1e_vi_display_phase.py --from 20
   --minrun 30 --thr 1.5 (level entries, and whether each entry has a Q gap >= 30 ms = hitch, or none = straddle) and the share of
   presents at level after 95 s (acq > 5).
   H-lock-prevents: LOCK arms have 0 hitch-free entries and less time at level; hitch (load) entries still occur in both.
   H-lock-neutral: same entries in both -> the level needs a drain anyway (ACQ=8 + LOCK combo becomes the recommendation).
   Note: the lock pauses while acq EMA > 5 ms, so a level formed at a load persists in LOCK arms without a drain; that is part of the
   answer, not a failure of the control. Control: [vi-lock] run=1 lines and W p50 ~10 in the non-level spans.
2. If 16:9 soaks show the same gain: add ROGUESQ_VI_LOCK=1 to the owner recipe line in OWNER-OPT-INS as a suggestion. Default stays
   off until the owner chooses.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
