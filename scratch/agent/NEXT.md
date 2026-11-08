# NEXT: G5i (OWNER PRIORITY 2026-11-08) - hangar fish-eye returns after an aborted mission
HYPOTHESIS-ID: g5i-hangar-reentry
Owner: G5g fix (s6907, ROGUESQ_G5G_AIM default on) looks good on first SELECT YOUR CRAFT entry; after
start mission -> abort -> back to hangar, the fish-eye is back and worse than retail.
Hypotheses (one run discriminates all):
- H-static: rs64_s6907_aim function statics (ps, act, fade, li, sc, t0, te, ds, lo; tools/apply_s6907_aim.py)
  carry stale scroll state across the hangar re-init -> re-entry log shows act/fade/t0 already set at
  entry, or t0/te from the old epoch (turn never runs or runs to the wrong time base).
- H-ram: 0x800CC3E4 state byte / 0x800CD6E8 cursor / 0x800CC404 craft table / 0x800CDA5C list mean
  something else after re-entry -> the aim target (destination craft position) differs from the
  craft actually drawn; off-axis stays high with aim "active".
- H-retail-worse: re-entry uses a different retail camera path (e.g. different eye path after abort),
  so the aim is applied to a path it was not tuned for -> G5G_AIM=0 same re-entry also shows a
  bigger off-axis than first entry.
Unit: ONE run, scratch/s6907/arm.zsh pattern, ROGUESQ_G5G_CAM=<file> plus a log line at every aim
(re)init dumping all statics and the 4 RAM words. Route: hangar, 3 scrolls, start mission (key drive),
pause+abort, hangar, 3 scrolls. Score each entry with tools/g5g_pan_score.py. Then the fix (reset the
statics on hangar entry, keyed on the state byte transition) and a same-binary =tog/before-after arm.
Close: re-entry off-axis numbers match first entry, owner sheet of re-entry mid-scroll frames.
Check screen unlocked (CGSSessionScreenIsLocked) before key-driven runs.
Deferred (was NEXT before s6994): G1e dense levels 7/16/17, slug g1e-dense-level-cost, CURRENT-TRUTH item 11.
