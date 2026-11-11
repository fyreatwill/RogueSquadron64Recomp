# NEXT: G3 in-flight owner-recipe fidelity at 21:9, remaining levels (CURRENT-TRUTH item 34)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7172): L0-L15 H-equal at 21:9. Next two: L16 and L17, then L18 (then close item 34 with a summary table).
Recipe (per level, one run at a time; check disk >= 20 GB free first, a cap is 12.6 GB; delete the .cap/.raw once the outliers are explained):
  env CW=504 CH=216 zsh tools/s7141_arm.zsh <lvl> L<lvl>w "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  zsh tools/s7141_post.zsh scratch/s7141 L<lvl>w 0,11,469,216 117,352   (check CONTROL PASS; _sh2 is the shift-2 positive control)
  python3 tools/s7163_rectfit.py scratch/s7141/L<lvl>w.raw scratch/s7141/L<lvl>wr scratch/s7141/L<lvl>w.frames.csv 0,11,469,216
  env SPLIT=117,352 SHEET_LABEL=21:9 zsh tools/s7160_fit_post.zsh scratch/s7141 L<lvl>w <bestrect> docs/owner_sheet_s71xx_L<lvl>_219_fidelity.png
  python3 tools/s7157_fsum.py scratch/s7141/L<lvl>w.frames.csv ; same for L<lvl>w_sh2.frames.csv  (note: needs the .frames.csv path)
Control power: on dark or smooth levels (L3, L8, L13) shift-2 gives 0 swaps >0.05; then judge by meand ratio plus the sheet.
Hypotheses per level: H-equal (centre frac <= ~0.015, no flight swap > 0.05 beyond lag/HUD), H-hole (wide-only clear/cull gap: tools/s7166_holetris.py),
H-lag (dup pframe). Score only the flight window; exclude medal/menu-JPEG swaps as s7163 did.
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM. CURRENT-TRUTH ~59.9 KB (<60000): keep edits net-neutral.
