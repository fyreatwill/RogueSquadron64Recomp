# NEXT: fold the s7128 W_SHEET_POS pixel soaks (dropped arm), then decide and send the owner sheet
HYPOTHESIS-ID: wsheet-escape
State (s7128): new trigger-ring recorder (ROGUESQ_G5B_FRAME_TRIG=<pre>,<post>, dpc_bridge.cpp) + ROGUESQ_W_SHEET_POS=t (drops in odd 24 MHz
seconds only; DROPLOG.pos field 11 = arm). Run t1: 5 detections, ALL arm 0 (kept). Along every wedge RT64 == angrylion (line |d| 0.3-1.3 =
control) and native angrylion draws nothing visible; painted-line positive control 6-11. The dropped arm (arm 1) is still unmeasured.
NOTE: CURRENT-TRUTH is 59.2 KB, just under the 60 KB maintenance trigger. Keep additions short, or this iteration becomes maintenance.
Step 1: read SOAK-RESULTS for s7128_wsheetpos_p1/p2 and scratch/s7128/p{1,2}_pixel.txt (last 3 lines = per-arm summary).
  The control is already in each file: arm 0 rows (kept) vs arm 1 rows (dropped), plus tools/s7128_ctl.py raw aldir pos swap pframe 0,9,369,216
  on one fire per arm (painted line must give |d| >> real).
Outcomes:
  H-fixed : arm 1 line |d| ~ control |d| (as in arm 0): dropping changes nothing visible. Close the wsheet-escape pixel check. The visible case stays
            the s7125/n1 escaper class (rare). Owner sheet: crops of the n1-style band (docs/owner_sheet_s7125_*) + s7128 fire frames.
  H-harm  : arm 1 line |d| >> control with AL showing terrain/colour RT64 lacks: tighten the rule (base <= 4 px, or clamp W instead of drop),
            re-run tools/s7128_arm.zsh 6 <name> "ROGUESQ_W_SHEET_POS=t ROGUESQ_G5B_FRAME_TRIG=6,4 ROGUESQ_W_SHEET_DROPLOG=... " 60 300.
  0 arm-1 fires in both soaks: queue 2 more (same recipe). Do NOT babysit them; if still none after 4, take arm-0 invisibility (two runs) as
  enough to close: the rule then only matters for the rare visible escaper, which s7127 logged.
Owner save rule applies (runner exports ROGUESQ_NO_SAVE_WRITE; never touch build/saves).
