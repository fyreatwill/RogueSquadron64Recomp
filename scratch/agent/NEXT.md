# NEXT: G3 in-flight owner-recipe fidelity at 21:9, remaining levels (CURRENT-TRUTH item 34)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7168): L0-L6 and L15 H-equal at 21:9. Next two: L7 and L8, then L9.. L18 (skip L15) two per iteration.
Recipe (per level, one run at a time; check disk >= 20 GB free first, a cap is 12.6 GB; delete the .cap once the outliers are explained):
  env CW=504 CH=216 zsh tools/s7141_arm.zsh <lvl> L<lvl>w "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  zsh tools/s7141_post.zsh scratch/s7141 L<lvl>w 0,11,469,216 117,352   (check CONTROL PASS; _sh2 is the shift-2 positive control)
  python3 tools/s7163_rectfit.py scratch/s7141/L<lvl>w.raw scratch/s7141/L<lvl>wr scratch/s7141/L<lvl>w.frames.csv 0,11,469,216
  env SPLIT=117,352 SHEET_LABEL=21:9 zsh tools/s7160_fit_post.zsh scratch/s7141 L<lvl>w <bestrect> docs/owner_sheet_s71xx_L<lvl>_219_fidelity.png
Control power: on dark levels (L3 s7168) shift-2 gives 0 swaps >0.05; then judge by meand ratio (tools/s7157_fsum.py on L<lvl>w and L<lvl>w_sh2) plus the sheet.
Hypotheses per level: H-equal (centre frac <= ~0.015, no flight swap > 0.05 beyond lag/HUD), H-hole (wide-only clear/cull gap: tools/s7166_holetris.py),
H-lag (dup pframe). Score only the flight window; exclude medal/menu-JPEG swaps as s7163 did.
Event-timed scenes: ROGUESQ_G5B_FRAME_TRIG=4,260 ROGUESQ_G5B_FRAME_TRIG_LB=1 records the first letterboxed cutscene after FROM.
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM. CURRENT-TRUTH ~59.9 KB (<60000): keep edits net-neutral.
