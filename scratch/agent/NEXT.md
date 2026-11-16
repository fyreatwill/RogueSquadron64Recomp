# NEXT (s7431)
HYPOTHESIS-ID: default-stderr-volume

First fold new scratch/agent/SOAK-RESULTS.md lines (s7428_audio_route_arms: rc 0 = F9 gate two-arm verified; 2 = VOID).

Class CN (CURRENT-TRUTH Next steps item 1): default-on stderr volume. s7430: a no-logging-env owner-recipe run
(ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_NO_SAVE_WRITE=1) writes ~1.5 MB per 40 s of boot.
Hypotheses: H-capped (every default-on tag has a per-run line budget; volume is boot-front-loaded and flight is quiet)
vs H-perframe (>=1 default-on tag prints per frame/task in flight: unbounded per run and a G5c H-log stall source)
vs H-burst (budgets exist but one event fans out to >100 KB in one frame).
Discriminating measurement, ONE run: forced-level route to flight (s5705-s5720 recipe, LEVEL=1, no keys needed?) for
>=180 s with stderr to a file, then offline: bytes per tag per 10 s window (boot / title / flight). A tag whose rate in the
last 60 s of flight is > 0 and flat = H-perframe. Static half: grep the top 15 tags' fprintf sites, record each budget
(counter cap or none) and gate. Positive control: plant ROGUESQ_<a known opt-in log>=1 and see its tag appear at its
expected rate. Fix: move per-frame/unbudgeted default-on tags behind an opt-in env (keep crash breadcrumbs default-on
but budgeted). Tool: tools/s7431_stderr_volume.py (exit 0 H-capped, 1 found, 3 control fail).
Reuse tools/s7430_file_growth.sh's copied-folder pattern (/tmp/rs64_s7430/R/1.runlog is a boot-only sample).
