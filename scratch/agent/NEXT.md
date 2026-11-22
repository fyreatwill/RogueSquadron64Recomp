# NEXT (s7793; s7792 compacted CURRENT-TRUTH to 23.4 KB)
HYPOTHESIS-ID: g3-frame-diff-unsheeted
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines (any of these outranks the rest).

Unit (CURRENT-TRUTH item 13): every ladder rung is closed or waiting on the owner. G3 render fidelity: find a level/scene with no
presented-frame angrylion diff since the s7122-s7217 matrix and the post-G6c tree (grep PORTING-STATE for "angrylion" + level), and
diff it at the owner recipe (16:9 dd1 control vs dd4 STANDINS=1) on the post-s7790 binary.
Hypotheses: H-equal (residual at the retail floor, as s7122-s7217), H-regress (a post-G6c/s7781-s7791 change moved the residual:
bisect by the =0 switch of each default-on fix touched since s7217).
Discriminator: per-frame residual vs the s7217 floor on the same phase-gated frames; positive control = a planted 1-tile diff must score.
The plume si_addr=0x58 is CLOSED (0/76 s7660, s7725 fix, NSZombie 0); queue a 20-boot non-recurrence soak only as a side job.
