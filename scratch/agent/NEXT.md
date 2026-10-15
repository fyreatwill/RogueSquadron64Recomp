# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4904: send_dl 23.2 ms = fullSync 11.3 + procDL-rest 7.0 + LLE RSP 4.8 + fbwait 0.8; logging overhead refuted (script scratch/agent/run_s4904_senddl_split.sh, S4267 timers).
The 30 Hz pacing is explained as host cost > 16.4 ms. Remaining question: what inside RT64 State::fullSync (11 ms) dominates — framebuffer/texture upload, draw-data/transform upload, or GPU wait (Metal)?
Hypotheses: H-fullsync-gpuwait (waits on prior frame GPU completion), H-fullsync-upload (CPU uploads), H-resolution (render scale/internal resolution large; try lower scale in one arm).
Discriminator: one build adding sub-timers inside lib RT64 State::fullSync (or first test existing config: run arms with RT64 resolution scale 1x vs current, concurrent) — if fullSync scales with resolution => GPU-bound/H-resolution.
Alternative if 30 Hz judged acceptable: park and return to M5 audio de-stub plan step.
