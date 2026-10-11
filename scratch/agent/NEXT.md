# NEXT: ground-truth the selected M4 VGE/store boundary
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4626 fixed the target-cap mistake by setting `ROGUESQ_M4_PHASE_FROM=5`.
The stage-1 positive control fired 64 rows; the qualified hangar phase emitted
517 stage-10, 517 stage-11, 517 stage-12, and 497 stage-13 rows. The local
VMADH reconstruction matched 4,128/4,128 paired lanes; 31 lanes changed
between post-VMADH and post-VGE. Retail independently reached hangar and its
whole-RDRAM control reached 10,000 callbacks. The active arm is VGE/store;
arithmetic is closed for this path.

Competing hypotheses:

- H-vge: post-VGE lanes differ from post-VMADH and the exact stored record
  bytes agree with post-VGE, selecting VGE semantics.
- H-store: post-VGE lanes are correct but the exact record bytes diverge,
  selecting the store/writeback path.
- H-source: the post-VGE lanes and record agree locally; only an independently
  attributed retail source/input transition remains divergent.
- H-instrument-boundary: the stage-1 control or phase-5 store join is absent;
  the result is unevaluable and selects no runtime hypothesis.

Discriminator: one batched phase-5 capture with the stage-1 control, all M4
stages, and exact record bytes; compare stage-12 `v6` to stage-13 record
lanes. Keep `ROGUESQ_M4_PHASE_FROM=5` so transient rows cannot consume the
target budget. The retail arm must carry the whole-RDRAM positive control and
VI trace; a missing target phase invalidates the comparison.

Exact commands:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run the canonical real-audio/LLE-ungated/LLE-solo/spin-yield route from
   `build/` with `ROGUESQ_LOG_M4_ACCUM=1`, `ROGUESQ_M4_CONTROL_CAP=64`,
   `ROGUESQ_M4_TARGET_CAP=2048`, `ROGUESQ_M4_PHASE_FROM=5`,
   `ROGUESQ_AUTOPILOT_STOP_WIDTH=0`, and the established autopilot schedule.
   Run the retail oracle in parallel with `--watch-write 0x0:0x800000`
   and `--vi-trace`.
3. Use a 120-second window, capture to a non-dot final path, and SIGKILL both
   processes. Report control count, phase-5 stage counts, VMADH mismatches,
   VGE deltas, and stored-record mismatches.
