# NEXT (s7796)
HYPOTHESIS-ID: g3-frame-diff-unsheeted
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines (any of these outranks the rest).

Unit (CURRENT-TRUTH item 13): post-G6c fidelity on L4 at 21:9, which crosses the mid-mission letterboxed cutscene (X-wing chased by TIEs
over water, swaps ~7885-8083 in s7165) whose lower-right hole s7166 fixed (SKYFILL_BOT). L1/L12 16:9 and L1 21:9 already == angrylion (s7793-s7795).
Screen unlocked (`/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'` must fail), one game:
  env RDIR=s7796 CW=504 CH=216 zsh tools/s7131_arm.zsh 4 L4w "ROGUESQ_ASPECT=21:9 ROGUESQ_STANDINS=1 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  (do NOT use tools/s7141_arm.zsh: it hard-codes scratch/s7141 and overwrites old files)
  zsh tools/s7141_post.zsh scratch/s7796 L4w 0,11,469,216 117,352
  env SPLIT=117,352 SHEET_LABEL=21:9 zsh tools/s7160_fit_post.zsh scratch/s7796 L4w 1,11,469,216 docs/owner_sheet_s7796_L4_219_standins_fidelity.png
  python3 tools/s7165_letterbox.py on the replay log (painted-of-total per swap) for the cutscene span; tools/s7165_rawlb.py on L4w.raw finds it.
Liveness: run.log under scratch/agent/m6/g1_lvl4s7131L4w/: `[standins] N objects`, `[g1d] ROGUESQ_ASPECT=21:9`, 0 CRASH lines.
Baseline s7165 L4w refit 1,11,469,216: frac 0.006/0.014/0.072, centre 0.006 side 0.006; 13 >0.05 all in the cutscene (pre-s7166 fix).
Hypotheses: H-equal (flight at the floor AND cutscene swaps <0.05 -> s7166 fix holds post-G6c), H-regress (flight moved: bisect via =0 switches),
H-cutscene (cutscene outliers back: compare ROGUESQ_HORIZON_SKYFILL=0 / SKYFILL_BOT switch in a second arm), H-standin (regions at stand-ins).
If the autopilot never reaches the cutscene (s7165 L4x0 voided this way), say so and score flight only; do not count it as a cutscene pass.
Delete .cap/.raw/replays after scoring (~15 GB) unless outliers need the stream (s7165 lesson: keep the .cap until outliers are explained).
If H-equal: the post-G6c fidelity thread closes; take the next ladder item from CURRENT-TRUTH (item 3c).
