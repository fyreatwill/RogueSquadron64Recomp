# NEXT (s7795)
HYPOTHESIS-ID: g3-frame-diff-unsheeted
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines (any of these outranks the rest).

Unit (CURRENT-TRUTH item 13): post-G6c fidelity at 21:9. s7793 (L1) + s7794 (L12) scored STANDINS=1 == angrylion at 16:9.
Run L1 at 21:9 (s7165 baseline), screen unlocked (`/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'` must fail), one game:
  env RDIR=s7795 zsh tools/s7141_arm.zsh 1 L1w "ROGUESQ_ASPECT=21:9 ROGUESQ_STANDINS=1 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  (check tools/s7141_arm.zsh head first: confirm the ASPECT in its XENV_EXTRA is overridden by the later $EX value, and the capture size for 21:9)
  zsh tools/s7141_post.zsh scratch/s7795 L1w 0,11,469,216 117,352
  env SPLIT=117,352 SHEET_LABEL=21:9 zsh tools/s7160_fit_post.zsh scratch/s7795 L1w 1,12,469,217 docs/owner_sheet_s7795_L1_219_standins_fidelity.png
Liveness: grep run.log under scratch/agent/m6/g1_lvl1*L1w/ for `[standins] N objects` and `[dd] multiplier 4` / 0 CRASH lines (the summary
file is not written; the arm's watchdog kills the common script first). Delete .cap/.raw/replays after scoring (~15 GB).
Baseline s7165 L1 21:9 refit 1,12,469,217: frac 0.009/0.010/0.011, 0 >0.05, centre 0.005, side 0.014, bands 3.47 3.23 2.55 2.47 3.10 3.33 3.93 9.28.
Hypotheses: H-equal (at the s7165 floor), H-regress (moved: bisect via =0 switches since s7217), H-standin (regions only at stand-ins,
esp. at the widened 21:9 sides). Discriminator: per-frame residual vs s7165 at the same rect + painted control PASS; worst-swap sheet
(expect CULL_SPIKE wedges as the only excess, as on s7794 L12). If H-equal, the post-G6c fidelity thread closes (L1+L12 16:9, L1 21:9):
take the next ladder item from CURRENT-TRUTH.
