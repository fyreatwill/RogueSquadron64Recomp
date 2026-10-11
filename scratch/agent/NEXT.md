# NEXT: repair the M4 DMEM store witness
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4627 requalified the route: stage-1 control 64; phase-5 stages
10/11/12/13 were 517/517/517/497. The corrected retail Rice oracle reached
512-wide `0x006AB400` and its whole-RDRAM control reached 10,000 callbacks.
The existing `record=` dump is invalid because `r9` is DMEM, not RDRAM.

Competing hypotheses:

- H-vge: DMEM bytes after the store agree with post-VGE lanes, selecting VGE
  semantics.
- H-store: post-VGE lanes are correct but the DMEM store bytes diverge,
  selecting store/writeback semantics.
- H-source: DMEM bytes agree locally; only an independently attributed retail
  source/input transition remains divergent.
- H-instrument-boundary: the corrected DMEM witness or phase-5 join is absent,
  selecting no runtime hypothesis.

Discriminator: one batched phase-5 capture with the stage-1 control, all M4
stages, and exact post-store bytes read from the RSP DMEM backing store at
`r9+0x18` (including the `sdv`/`ssv` overwrite lanes); compare stage-12 `v6`
to stage-13 DMEM bytes. Keep `ROGUESQ_M4_PHASE_FROM=5` so transient rows
cannot consume the target budget. The retail arm must carry the whole-RDRAM
positive control, verified Start schedule, and VI trace; a missing target
phase invalidates the comparison.

Exact commands:

1. Patch the existing probe in `src/rsp/dpc_bridge.cpp` to dump the actual
   RSP DMEM bytes, not `rdram[r9+...]`; rebuild once.
2. Run the canonical real-audio/LLE-ungated/LLE-solo/spin-yield port route
   from `build/` with `ROGUESQ_LOG_M4_ACCUM=1`, `ROGUESQ_M4_CONTROL_CAP=64`,
   `ROGUESQ_M4_TARGET_CAP=2048`, `ROGUESQ_M4_PHASE_FROM=5`,
   `ROGUESQ_AUTOPILOT_STOP_WIDTH=0`, and the established autopilot schedule.
   Run the retail oracle with `--watch-write 0x0:0x800000`, `--vi-trace`, and
   the verified `--press 6:start,11:start,...,71:start` schedule.
3. Use a 120-second window, capture to non-dot final paths, SIGKILL both
   processes, and report control count, stage counts, VGE deltas, and DMEM
   store mismatches.
