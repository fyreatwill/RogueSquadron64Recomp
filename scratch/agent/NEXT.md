# NEXT: G3 in-flight fidelity at RETAIL settings (4:3, dd1, no FPS60): L8, L9, L10 (CURRENT-TRUTH item 36)
HYPOTHESIS-ID: g3-retail-43-sweep
State (s7175): retail 4:3 H-equal on L0-L7. Remaining: L8-L18.
Run (one game at a time; the offline post of level N can overlap the run of level N+1):
  env CW=320 CH=240 zsh tools/s7141_arm.zsh <lvl> L<lvl>r "ROGUESQ_FPS60=0 ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_ASPECT=4:3 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  Check scratch/s7141/cap_L<lvl>r.txt says window (..., 1062.0, 828.0); if the size differs, refit the rect from scratch.
Post: zsh tools/s7141_post.zsh scratch/s7141 L<lvl>r 0,10,308,241 103,205
  python3 tools/s7157_fsum.py scratch/s7141/L<lvl>r.frames.csv scratch/s7141/L<lvl>r_sh2.frames.csv
  python3 tools/s7163_rectfit.py scratch/s7141/L<lvl>r.raw scratch/s7141/L<lvl>rr scratch/s7141/L<lvl>r.frames.csv 0,10,308,241 --every 8   (CTRL must PASS)
  env SPLIT=103,205 SHEET_LABEL=4:3 zsh tools/s7160_fit_post.zsh scratch/s7141 L<lvl>r <best rect> docs/owner_sheet_s717x_L<lvl>_43_fidelity.png
Hypotheses per level: H-equal (centre <= ~0.015, 0 flight >0.05 beyond lag/HUD), H-hole (tools/s7166_holetris.py), H-lag (dup pframe), H-tool (CTRL fails / shift-2 no worse).
Shift-2 is the positive control; dark levels judged by meand ratio + sheet. L17: FROM=4700, arm delay 60 (trench autopilot fails ~126 s).
Disk: each run is 12.6 GB cap + 2.2 GB raw; check df >= 20 GB before each run and rm .cap right after its post. Delete .raw after the sheet.
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM. CURRENT-TRUTH ~60.0 KB: keep edits net-neutral (if Step 0 trips >60000, do maintenance first).
