# NEXT work unit (s2659) — map the next M5 output boundary

HYPOTHESIS-ID: m5-output-boundary-mapping

## Work unit

Perform one ground-truth/static mapping census of the already observed M5
output spans, not another task-field watch: correlate retail writer PC
`0x800078EC` and its secondary-span writers with port image DMA ranges
(`0x168xxx` and `0x1798B0:0x179A48`) and CPU MORT/PCM source-consumer rows.
No runtime behavior change, writeback, remap, or gate change is allowed.

## Competing hypotheses and discriminator

- `H-ImageOutputEdge`: retail writers map to the Factor 5 image output span;
  port DMA payload/destination is the missing contract edge.
- `H-CPU-MORT-Edge`: retail writers map to CPU MORT publication; the image
  task is not the PCM producer.
- `H-ConsumerOnlyGap`: the port has a legitimate nonzero source, but the
  source-to-consumer/AI boundary loses it.
- `H-Unmapped`: current observations do not provide a complete mapping.

The discriminator is one table keyed by phase and output span containing
retail writer PC/count/value polarity, port DMA destination/length/hash/nz,
port PCM source and consumer spans/hash/nz, MORT descriptor class, and
ordering relative to task completion. Select only if one hypothesis has a
complete mapping; otherwise record `H-Unmapped` and pivot to a named missing
edge. Require the existing oracle whole-RDRAM/route controls and paired port
image/silent phase controls.

## Exact commands

1. Read `scratch/agent/s2658_m5_task_output_fields_retry/audit.md`,
   `docs/M5-AUDIO-PLAN.md`, and bounded excerpts from s2614/s2619/s2620.
2. Build no code unless the census identifies a diagnostic source already in
   the fixup pipeline. Do not add another task-field watch.
3. Write the complete table and selected/unevaluable hypothesis to
   `scratch/agent/s2659_m5_output_boundary/audit.md`.

## Expected outcomes

- A complete retail-to-port destination/value/order match selects one named
  edge and defines the next single behavior change with rollback.
- A nonzero port source with a missing consumer join selects
  `H-ConsumerOnlyGap` and scopes the next host/AI boundary test.
- Zero/ambiguous payloads or no complete cross-source match selects
  `H-Unmapped`; do not implement mitigation or writeback.
