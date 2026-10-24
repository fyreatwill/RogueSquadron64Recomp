# NEXT: G1c phase 2 - push draw distance (per ITERATION.md 3c)
HYPOTHESIS-ID: g1c-phase2-drawdist
Start from s6074 state (DRAW_DISTANCE=2 + auto-far; px3+ exhausts 8 MB guest heap, s6062).
Unit: find the binding limit at DD=3 on lvl1: carve terrain pools from 0x80800000+ (librecomp maps 512 MB behind rdram; keep gfx-read data below 0x81000000). Hypotheses: H-heap (rs_malloc exhaustion), H-ucode-cap (ROGUESQ_UCODE_CAP), H-stride (64-wide bitmap/terrain dims, s6035). Discriminator: DD=3 with a second arena at 0x80800000 -> heap-failure log gone? then next limit shows.
Measure with the fixed-camera terrain-fraction scorer + contact sheet dd1 vs dd-max.
G3b is closed (s6085); do not reopen without owner report.
