# NEXT (s7794)
HYPOTHESIS-ID: g3-frame-diff-unsheeted
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines (any of these outranks the rest).

Unit (CURRENT-TRUTH item 13): second level for the post-G6c fidelity claim. s7793 scored L1 STANDINS=1 == angrylion (H-equal).
Run L12 (s7159 baseline; refit rect 0,10,370,217 is the s7160 default) at the same recipe, screen unlocked, one game:
  env RDIR=s7794 zsh tools/s7131_arm.zsh 12 L12s "ROGUESQ_STANDINS=1 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  zsh tools/s7141_post.zsh scratch/s7794 L12s 0,9,369,216 46,322     # JOBS=2 default
  zsh tools/s7160_fit_post.zsh scratch/s7794 L12s 0,10,370,217 docs/owner_sheet_s7794_L12_standins_fidelity.png
Check run.log for `[standins] N objects` (N>0) and `[dd] multiplier 4`. Delete .cap/.raw/replays after scoring (~15 GB).
Hypotheses: H-equal (residual at the s7159/s7160 floor), H-regress (moved: bisect via =0 switches of fixes since s7217),
H-standin (regions only where stand-in models sit: compare with a STANDINS=0 arm in the same iteration).
Discriminator: per-frame residual vs s7159 L12 at the same rect; painted control must PASS. If L12 is H-equal, the post-G6c claim is
two-level; do the same at 21:9 (SPLIT=117,352 SHEET_LABEL=21:9, s7165 recipe) on L1 next.
