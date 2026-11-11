# NEXT: G3 mission intro cutscene at 21:9, two arms: default vs ROGUESQ_VI_EXACT_ROWS=1 (CURRENT-TRUTH item 37)
HYPOTHESIS-ID: g3-intro-219-exact-rows
State (s7148): the intro cutscene (space flyby 9860-10350, sea/AT-AT cinematic 10400-13450, flight 13520+) is RT64 == angrylion at 16:9
after one fit, but every phase needs y-scale e 0.980-0.984 = angrylion's 300 rows vs 294 (VI) / 296 (RT64 fbSize) presented rows.
s7147's ROGUESQ_VI_EXACT_ROWS=1 makes RT64 present the VI's 294 rows; on crawl glyphs it could not be pixel-qualified (e and sy trade off).
The planet limb (space phase) is a sharp, wide y target.
Step 1, two runs one after the other (one game at a time), 21:9 capture 504x216:
  env RDIR=s7149 ASP=21:9 SECS=275 FROM=9750 EVERY=10 DL=150 DU=115 AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a zsh tools/s7146_arm.zsh T1 ""
  same with name T2 and extra env "ROGUESQ_VI_EXACT_ROWS=1"
  (check window in cap_T1.txt; s7141 21:9 rect 0,11,469,216 split 117,352 — re-derive if the window differs).
Step 2: zsh tools/s7141_post.zsh scratch/s7149 T1 <rect> <split> (and T2); phase csvs by swap range; tools/s7148_pfsearch.py per phase;
  joint fit (scratch/s7148/fitrun.py pattern, JR=<rect>, JK=1.0, JE 0.976..1.004, JY -4..8, JX 0..2) per arm per phase. Delete .cap after.
Hypotheses / outcomes:
  H-rows294 (hardware shows 294 rows; EXACT_ROWS is right): T2 identity frac lower than T1 and T2's best e is the one predicted for 294 rows
    with sy ~0 on the limb; T1 needs the extra e/sy term.
  H-rows296 (RT64's 296 matches what the model frame implies): T1 fits with less offset than T2.
  H-trade (e/sy degenerate even on the limb): both arms reach the same floor with different (e, sy) -> EXACT_ROWS stays opt-in, record that
    pixels cannot decide and stop the thread.
Also report 21:9 per-phase fitted frac vs the 16:9 numbers (H-equal at 21:9 for the cutscene).
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Keep CURRENT-TRUTH under 60000 B (58.3 KB now).
Note: scratch/s7148/C2.cap (14 GB, unscored leftover of an interrupted attempt) can be deleted if disk gets tight (63 GB free at s7148).
