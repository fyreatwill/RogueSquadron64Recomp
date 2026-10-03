# Next work unit: M5 target-phase RSP audio-DMA descriptor census

HYPOTHESIS-ID: m5-alternate-family-object-route-join

The corrected s3828 route witness was target-valid and all route controls were
positive, but exact-route DMA and source-range reader/writer rows were zero.
Do not interpret alternate-object ownership until the missing DMA witness is
explained.

Competing hypotheses and discriminator:

- H1: target-phase RSP audio DMA occurs, but its RDRAM/DMEM span misses the
  current `0x1797B0..0x179A48`, `0x6F0..0x9F0`, and `0xCB0..0xE48` windows.
- H2: target-phase RSP audio DMA does not occur after route preparation; the
  route handoff is disconnected from the audio task.
- H3: the DMA callback census is itself not live or is phase-gated incorrectly.

The discriminator is one target-valid image run with a bounded, phase-scoped
census of every `rs64_m5_audio_source_dma` call (dram, len, dmem, route
ordinal/row, phase, and target key), plus the existing whole-RDRAM/phase,
route-prep/order/transition/handoff, and DMA-hook positive controls. H1 is a
target-phase DMA row outside the current windows; H2 is route controls plus no
target-phase DMA rows; H3 is a missing callback positive control or missing
target phases.

Before running, add the census to the existing callback and build:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run the corrected harness from `build/` with SIGKILL cleanup. Keep
`PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1`, the validated autopilot,
`ROGUESQ_LOG_M5_RSP_SOURCE=1`, `ROGUESQ_LOG_M5_ROUTE_PREPARE=1`,
`ROGUESQ_LOG_M5_ROUTE_ORDER=1`, `ROGUESQ_LOG_M5_ROUTE_TRANSITION=1`,
`ROGUESQ_LOG_M5_ROUTE_HANDOFF=1`, and `ROGUESQ_LOG_M5_EXACT_ROUTE=1` enabled.
