# NEXT: G3 in-flight owner-recipe fidelity at 21:9, remaining levels (CURRENT-TRUTH item 34)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7166): L1, L4, L6, L15 H-equal at 21:9; the L4 cutscene hole is fixed (SKYFILL_BOT, s7166, owner look pending).
Next: sweep the other 15 levels, two per iteration, same recipe as s7165 L1:
  tools/s7141_arm.zsh <lvl> <name> "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000" (CW=504 CH=216)
  post rect 0,11,469,216 split 117,352, refit with tools/s7163_rectfit.py, `env SPLIT=117,352 SHEET_LABEL=21:9 tools/s7160_fit_post.zsh`.
Hypotheses per level: H-equal (centre frac <= ~0.015, no flight swap > 0.05 beyond lag/HUD), H-hole (a wide-only clear/cull gap: check
with tools/s7166_holetris.py rects vs magenta bbox via the s7166 method), H-lag (dup pframe). Score only the flight window.
Event-timed scenes: ROGUESQ_G5B_FRAME_TRIG=4,260 ROGUESQ_G5B_FRAME_TRIG_LB=1 records the first letterboxed cutscene after FROM.
Also worth one look: other letterboxed cutscenes at 21:9/16:9 that SKYFILL touched before s7166 (same bug class, now fixed by construction).
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM. CURRENT-TRUTH ~59.7 KB (<60000): keep edits net-neutral.
