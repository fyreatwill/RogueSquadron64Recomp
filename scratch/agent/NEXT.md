# NEXT: is the eye-cell near-plane clip (the "FPS60 near-wall flicker") retail game behaviour?
HYPOTHESIS-ID: fps60-wall-retail
Context (s7108): the push-out corner width (0.86 of the projection, the same at 4:3), near distance (30 = 30) and the 60 fps tick
(stream losses 49/49 at lim2 in s7108; 30 lim1 / 27 lim2 in s7107) are all refuted. The clip is static-recompiled retail camera
logic meeting canyon walls, so it may happen in retail too.
Unit: one run, L6, retail settings, same instruments, no CAMWIDE:
  copy scratch/s7099/arm.zsh to scratch/s7109/arm_retail.zsh, drop ROGUESQ_DRAW_DISTANCE/ROGUESQ_ASPECT from XENV_EXTRA (dd1, 4:3),
  and make sure ROGUESQ_FPS60 is unset/0 (check what g1_level_coverage_common.zsh exports first); keep G3C_LOG, S7101_CHASE,
  S7106_RSPTRI, S7107_TAG, G5B_TRIS. g5b_capture size must follow the 4:3 window (check the window line in cap_*.txt).
  Then: tools/s7107_losscan.py tris.bin drops.csv > losscan; count eye-cell near-z rows (ref c+0+0, drop minz < 0x100) per
  wall-hug minute, against s7108's 49 / ~90 hug-min-equivalent numbers (tools/s7108_split.py prints hug s per state).
Hypotheses:
 H-retail  eye-cell near-z losses at retail settings at a similar per-hug-minute rate -> retail behaviour; report to the owner with
           a sheet (tools/s7107_sheet.py) and offer an opt-in fix (e.g. a bigger push margin, or a lower near plane via ROGUESQ_DD_NEAR)
 H-opt     ~0 losses at retail settings while the camera hugs walls -> an opt-in (dd>1 far/near scaling, 16:9 viewport) owns it;
           bisect by adding dd4, then 16:9
Positive control: losscan must flag the s7108 swaps when rerun on s7108 data (49 eye rows), and the retail run must show wall-hug
seconds > 30 (else the null is from not hugging walls).
