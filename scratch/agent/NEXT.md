# NEXT: G3 in-flight fidelity at RETAIL settings (4:3, dd1, no FPS60) beyond L1/L6 (CURRENT-TRUTH item 36)
HYPOTHESIS-ID: g3-retail-43-sweep
State (s7173): owner-recipe fidelity closed at 16:9 (item 33) and 21:9 (item 34) on L0-L18. Retail settings only checked on L1 (s7122) and L6 (s7124).
Recipe: reuse tools/s7141_arm.zsh; its XENV_EXTRA sets FPS60=1 DD=4 ASPECT=16:9 and then appends EX, so pass overrides in EX:
  env CW=<4:3 width> CH=<h> zsh tools/s7141_arm.zsh <lvl> L<lvl>r "ROGUESQ_FPS60=0 ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_ASPECT=4:3 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  First: verify the override really wins (grep the env echo in scratch/agent/m6/g1_lvl<lvl>s7141L<lvl>r/run.log for ASPECT/FPS60) and take
  CW/CH + compare rect from s7122/s7124 (PORTING-STATE "## Session 7124": rect 20,15,279,240 at 320x240 capture; s7123: SCK pads the right).
  Then s7141_post (rect, split = the 4:3 centre/side thirds), s7163_rectfit, s7160_fit_post with SHEET_LABEL=4:3, s7157_fsum on .frames.csv and _sh2.
Order: L0, L2, L3, L4, L5 first (2-3 levels per iteration), then L7-L18. L17: use FROM=4700 with arm delay 60 (trench autopilot fails at ~126 s).
Hypotheses per level: H-equal (centre frac <= ~0.015, no flight swap > 0.05 beyond lag/HUD), H-hole (cull/clear gap: tools/s7166_holetris.py),
H-lag (dup pframe), H-tool (rect/registration wrong at 4:3: rectfit CTRL must PASS). Shift-2 (_sh2) is the positive control; dark levels need meand ratio + sheet.
Check disk >= 20 GB free before each run (cap 12.6 GB + raw 4.3 GB); delete .cap/.raw once outliers are explained. zsh: `rm` with an unmatched glob aborts the whole line.
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM. CURRENT-TRUTH ~59.9 KB (<60000): keep edits net-neutral.
