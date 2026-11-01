# NEXT: G1e frame rate on the -O2 build — what binds FPS60 below 60
HYPOTHESIS-ID: g1e-fps60-o2

G1c phase 2 closed s6703 (sheets docs/img/g1c_phase2_dd_sheet_vi*.png, docs/DRAW-DISTANCE.md). Ladder: G1d/G1f/G3c/G3d closed,
so G1e (higher frame rate) is the next open rung. s6702: FPS60 dd4 lvl5 ~45 tasks/s on -O2. Unknown: FPS60 at dd1 (retail draw).

Queued soaks (loop runs them): s6703_fps60_dd1_lvl1, s6703_fps60_dd1_lvl5 (ROGUESQ_FPS60=1, STORE_DIAG=0, G1B on, 300 s).
1. Fold both: game tasks/s, gfx task ms p50/p90, present-interval distribution, crash/stall (same G1B fold as s6697/s6701).
2. Hypotheses for any shortfall below ~58 tasks/s:
   H-gfx: gfx task ms p50 > ~16 ms (RSP LLE cost binds) -> profile the ucode loop (perf/sample on the RSP thread).
   H-cpu: gfx task < 12 ms but the game thread is busy >16 ms per frame -> sample the game thread (sample(1) 10 s), name the top
          host functions.
   H-pace: both under budget but tasks bunch / wait on VI -> FPS60 divisor/VI-delivery path.
   Discriminator: per-frame gfx ms vs game-thread busy ms, from the same run.
3. If dd1 FPS60 already holds ~60 on both levels, record it in docs/OWNER-OPT-INS.md (FPS60 row) as the recommended combo and
   measure FPS60+dd2 next.
