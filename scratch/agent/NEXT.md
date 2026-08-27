# NEXT work unit (s2615) — map the retail PCM writer family to the port

HYPOTHESIS-ID: m5-audio-contract-output-edge

## Single work unit

Add one regeneration-safe, phase-gated port witness for every direct guest
store/copy edge that can publish into the two PCM spans, keyed by destination
physical address, guest PC, value, and task/event ordinal. Cover the retail
writer-family candidates `0x800078EC`, `0x80007670`, `0x8001E2C0`, and
`0x8001FAxx–0x8001FD2C` in the generated/fixup source before running. Retain
the existing image-stage, DMA, task-join, PCM source/consumer, and host-writer
controls in the same Debug run; do not change C88, audio dispatch, or output
routing.

## Competing hypotheses and discriminator

- `H-PortEquivalentWriter`: a legitimate port guest writer reaches the retail
  PCM spans with nonzero values before consume.
- `H-PortPublicationGap`: no legitimate port writer reaches those spans before
  consume, despite the live image/task path.
- `H-JoinAccountingGap`: a matching port writer exists and values agree, but
  task/event ordering is the only reason the current join remains incomplete.

The discriminator is one phase-keyed table for title `1024/0x00790400` and
hangar `512/0x006AB400`: each candidate writer's destination/value/PC, exact
PCM source and consumer span/hash, image DMA source/destination/hash, and
task/event ordering. A positive nonzero guest-writer row at a valid PCM
destination selects the equivalent-writer hypothesis; zero candidate rows
with live controls selects the publication gap; matching writer/value/hash
rows with order-only mismatch selects accounting. Do not infer legitimacy
from a host `copyToRAM` row alone.

## Exact checks

1. Enumerate the candidate store/copy sites in the generated/fixup sources and
   add the bounded witness; run the generator/fixup validation so it survives
   regeneration.
2. Build with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. From `build/`, run 90 seconds with `ROGUESQ_LLE_FORCE=1`,
   `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_LOG_ALL=1`, the compiled default C88, and
   `ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`;
   do not set `ROGUESQ_AUTOPILOT_STOP_WIDTH`. Kill with SIGKILL and capture
   under `scratch/agent/s2615_m5_port_writer_family/`.
4. Require positive controls, both target phases, and report candidate writer
   rows, nonzero/hash correspondence, join closure, and crash/abort/missing-
   function counts.
