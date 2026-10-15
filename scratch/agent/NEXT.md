# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4902: port swaps at ~30 Hz (dt med 33.35 ms) over 60 Hz retraces (16.4 ms); swap lands 0-11 ms (med 3.8) after the 2nd retrace. H-vi-rate refuted; leans H-slow-frame over H-divider.

Hypotheses: H-slow-frame-gfx (frame bounded by gfx task completion latency in the port's RSP/RDP emulation); H-slow-frame-other (audio/spin-yield/mutex wait in game thread); H-divider (game-side limiter; swap would sit ~0 ms after R2 — mostly disfavoured).
Discriminator: one run, extend tools/apply_s4902_swap_timing.py: timestamp gfx-task-done (DP/SP-done message to the game queue) and the osSendMesg/recv wait points of the game main loop; per origin-change row log ms of task-done relative to R1/R2/swap. Task-done before R1+16.7 => game-side wait (H-divider/other); after => H-slow-frame-gfx. Positive control: the existing R/S events must still fire in the same row.
