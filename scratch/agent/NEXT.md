# NEXT: G3d close-out on the fixed build, then dd cost re-baseline
HYPOTHESIS-ID: g3d-turning-shake-timing

s6696 fixed the cause: our s6372 per-vector-load getenv + s6375 unarmed SDV snapshot made gfx tasks ~5x slower
(lvl1 29.7 -> 17.6 game fps, bunched presents). Same-run toggle (ROGUESQ_G3D_LEGACY_TOGGLE=<sec>) + census
(tools/g3d_g1b_census.sh, tools/g3d_toggle_fold.py).

Work unit (one run, two arms in-process where possible):
1. Re-run the s6455 jerk arms on the fixed build (retail and FPS60, lvl1 steady turn, ROGUESQ_G3C_LOG=1;
   tools/g3c_jerk.py). Hypotheses: H-fixed (shake was the 17 fps bunching; retail now shows even 16.5 ms presents
   and jerk only at the 30 Hz game-frame cadence), H-residual (sign-alternating camera jerk remains at 30 fps:
   FPS60/camera cadence issue, G3c(c) leads). Discriminator: present-interval p95 <= 34 ms and no
   sign-alternating jerk in retail -> H-fixed; else H-residual with the arm that owns it.
2. Re-baseline dd4 lvl1 + lvl5 cost with ROGUESQ_G1B (s6390-s6582 cost tables are void); record tasks/s and
   sd_wall for dd1/dd4 and update docs/DRAW-DISTANCE.md if the dd4 trade-off changed.
Owner: judge turning feel on the fixed build; send s6694/s6695 21:9 level-select frames.
