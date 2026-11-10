# NEXT: FPS60 near-wall flicker: name the camera push-out writer and read its step
HYPOTHESIS-ID: fps60-wall-camera
Context (s7100): H-push selected on two lines. The per-tick episode rate is 4.1x higher at lim=1 (60 fps windows), p=0.033 over 4 runs, and the
eye (0x80130C10, the terrain builder's copy of the camera position) zig-zags every tick at 60 fps episodes while the retail-rate episodes are clean
stops. Recipe: scratch/s7099/arm.zsh 6 4 <tag> "ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600 ROGUESQ_G3C_LOG=1" 120 240 (L6 dd4 16:9, FPS60 off).
Unit (one build, one run):
 1. Offline first: find the caller(s) of buildVisibleTerrainGridAroundCamera and where its a0 eye comes from (the camera object position).
    Then grep-enumerate the stores to that camera position and the terrain-height / wall query the camera code calls (push-out candidates).
 2. One build: log per tick (lim, eye before and after each candidate store, the store PC, the step size) at L6; positive control = the
    log must show the ordinary follow-camera store on every tick.
 3. At each episode tick (tools/s7100_episode_eye.py lists them), read which store moved the eye back and forth.
Hypotheses for the writer:
 H-pushfix  a fixed-fraction push-out (e.g. move 1/2 of the penetration per tick) applied with a dt-scaled follow: at 1/60 the follow
            re-enters the wall every other tick -> fix: scale or iterate the push-out per real time, or clamp to the surface fully
 H-order    the follow and the collision run in a different order on render-only (60 Hz) ticks than on sim ticks -> fix: run the collision after
            the follow on every tick
Outcomes: the zig-zag store PC and its formula; then a fix behind ROGUESQ_S7101_CAMPUSH=tog with a same-run episode count (needs >=2x drop).
Note: the s7099 soak scripts delete their raw capture; keep the raw this time so the baseline can be wall-hug-conditioned.
