# NEXT: fold dd4 lvl10 + dd6 lvl1/lvl5 soak verdicts (G1c phase 2)
HYPOTHESIS-ID: g1c-dd4-limits
Hypotheses: H-dd6-clean (dd6 holds like dd4), H-limit (heap alloc failure, ucode cap, VI<60, or crash at dd5/6), H-no-effect (log must say "multiplier 6" else clamp patch didn't take).
Steps: read tail of scratch/agent/SOAK-RESULTS.md for s6461_dd4_lvl10 / s6462_dd6_lvl1 / s6462_dd6_lvl5; grep their logs for 'multiplier', crash lines, vi stalls, alloc failures, VI mean, sd_wall. If dd6 clean, make contact sheet dd1 vs dd6 same camera for owner; if limit hit, name the writer and fix root cause. Then continue to dd8 or the next limit.
