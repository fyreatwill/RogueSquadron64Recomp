# NEXT: fold g1_lvl10_pu / g1_lvl15_pu, then G1 (c)+(d) for level 1

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold the two _pu verdicts from SOAK-RESULTS (ROGUESQ_FORCE_PLANET_UNLOCK=0xFF). Pass = flight + 300 s hold,
0 crash/stall within ~400 s => unlock-bit gate confirmed; use the lever for 10/15 from now on.
Fail (viewer persists) => gate refuted; read runModelViewerLoop G2 timer instead.
Then: framebuffer capture in flight for level 1 + forced-hit objective response (no aim work).
