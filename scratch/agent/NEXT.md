# NEXT: G3 in-flight fidelity at RETAIL settings (4:3, dd1, no FPS60): L17, L18 (CURRENT-TRUTH item 36)
HYPOTHESIS-ID: g3-retail-43-sweep
State (s7178): retail 4:3 H-equal on L0-L16. Remaining: L17, L18 (then item 36 closes; take the next CURRENT-TRUTH step).
FIRST: Step 0 — CURRENT-TRUTH is 59992 bytes, so any net growth trips the >60000 maintenance check. If wc -c says >60000, do the maintenance iteration instead.
Run (one game at a time; the offline post of level N can overlap the run of level N+1):
  env CW=320 CH=240 zsh tools/s7141_arm.zsh <lvl> L<lvl>r "ROGUESQ_FPS60=0 ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_ASPECT=4:3 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  Check scratch/s7141/cap_L<lvl>r.txt says window (..., 1062.0, 828.0); if the size differs, refit the rect from scratch.
Post (ALWAYS with FID_MAINRUN=1, s7177: some fbs paint stray rows under the VI band and the default crop squashes them):
  env FID_MAINRUN=1 zsh tools/s7177_post_lvl.zsh <lvl>        (prints CONTROL, fsum main + shift-2, rectfit; CTRL must PASS)
  env FID_MAINRUN=1 SPLIT=103,205 SHEET_LABEL=4:3 zsh tools/s7160_fit_post.zsh scratch/s7141 L<lvl>r <best rect> docs/owner_sheet_s717x_L<lvl>_43_fidelity.png
Hypotheses per level: H-equal (centre <= ~0.015, 0 flight >0.05 beyond lag/HUD), H-hole (tools/s7166_holetris.py), H-lag (dup pframe, or
the swap's image appears in a later pframe only: score it against neighbouring pframes as s7177 did for L12 8069), H-tool (CTRL fails / shift-2 no worse / row-gap crop).
Shift-2 is the positive control; dark levels judged by meand ratio + sheet. L17: FROM=4700, arm delay 60 (trench autopilot fails ~126 s).
Disk: each run is 12.6 GB cap + 2.2 GB raw; check df >= 20 GB before each run and rm .cap/.raw right after the sheet.
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM.
L16 lesson (s7178): if the capture window holds a static results screen, judge the shift-2 control on flight swaps only (split the frames.csv by swap range).
