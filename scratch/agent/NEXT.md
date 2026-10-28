# NEXT: confirm span-bypass frame cost same-run, then cut it
HYPOTHESIS-ID: g1c-span-reject-predicate
s6535 (cross-run, single-source): dd4 bypass lvl1/lvl5 gives ~10 gfx tasks/s, 103-110 ms/task vs opt-out 14-16 tasks/s, 62-70 ms. Iron rule 2 forbids trusting cross-run on animating scenes.
Hypotheses: H-more-tris (bypass accepts many more cells -> more RSP work, expected cost, tune a cap); H-pose (runs differ in scene); H-bypass-overhead (per-cell host cost).
Discriminator: pinned lvl1 dd4 with ROGUESQ_G1B=1 ROGUESQ_SPANFORCE=toggle (s6528 recipe, tools/apply_s6527_spanforce.py), per-second g1b lines aligned to toggle swaps; compare tasks/s and sd_wall in force-on vs off windows within one run. Positive control: the toggle must change terrain fraction (s6528 did 0.047 vs 0.209).
If cost is in force-on windows only -> H-more-tris: add a cell-count/radius cap (e.g. ROGUESQ_BYPASS_MAXCELLS) inside DRAW_DISTANCE and re-measure per step.
Put ROGUESQ_G1B=1 into XENV_EXTRA; g1b lines land in scratch/agent/m6/<TAG>/run.log.
