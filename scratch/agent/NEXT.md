# NEXT (s7919)
HYPOTHESIS-ID: ladder-recheck-s7919
s7918 maintenance done (CURRENT-TRUTH 29576 B). Every ladder rung is closed or awaiting the owner (docs/OWNER-REVIEW-QUEUE.md).
1. `python3 tools/crash_reports.py --since 2026-11-22`; check owner answers in OWNER-REVIEW-QUEUE.md / ITERATION.md; tail SOAK-RESULTS.
   A NEW crash report outranks everything (s7664).
2. Otherwise take ITERATION 3c's first non-closed rung: re-check G5c freeze-gap / G1e present cadence on a fresh owner-recipe soak
   (FPS60=1 DD=4 ASPECT=16:9, no logging env, present ring). Hypotheses: H-clean (no gap >250 ms outside loads, max_gap ~148 ms as
   s7802/s7809) vs H-regress (a gap >250 ms or vi_stalls30s>0 since s7840-s7917 runtime edits: DET_CLOCK, CLOCKLOG hooks in
   librecomp ultra_translation.cpp). Discriminator: ring_stalls.py max gap + vi_stalls30s on the default (DET_CLOCK unset) binary,
   with a positive control (planted 300 ms stall in the ring read must be caught). Queue it as a soak with SOAK_NEEDS_IDLE if host busy.
