# NEXT work unit (s2678) — audit the downstream MORT voice consumer

HYPOTHESIS-ID: m5-audio-cpu-mort-publication-boundary

## Work unit

Perform one bounded source audit after `filterVoiceSampleBlock` /
`applyVoiceDelayFilter`: identify the next named downstream voice consumer,
its caller, persistent input/output structure, and one source-derived
destination. Ask the retail oracle about that destination with the
whole-RDRAM positive control and target phase. Do not change runtime behavior,
add writeback, or repeat task-field, image-ring, or shared-stack censuses.

## Competing hypotheses and discriminator

- `H-MORT-edge`: a persistent destination has a target-phase writer/order join
  to PCM.
- `H-image-edge`: the MORT relation is absent, while the Factor 5 image has a
  complete consumer join.
- `H-MORT-unmapped`: the downstream value is temporary/shared or lacks a
  legitimate payload/order join.

The discriminator is one table covering caller/entry, source-derived
destination, descriptor/type, payload polarity, target-phase writer rows,
port PCM source/consumer events, image completion, and ordering. A complete
CPU join selects `H-MORT-edge`; a complete image join selects `H-image-edge`;
missing writer or ordering selects `H-MORT-unmapped`. A narrow null is invalid
unless the same oracle run visibly fires its whole-RDRAM control and reaches
the target phase.

## Exact commands

1. Use bounded `rg`/`sed` reads of companion mappings and generated source for
   the filter, its callers, and the next named consumer.
2. Read `tools/oracle/README.md`; choose the smallest source-derived
   `--watch-write` and any needed `--watch-pc`. Ask ground truth before adding
   port instrumentation.
3. Run one batched oracle capture only after the positive-control and phase
   gates are armed. Record the table and artifact under `scratch/agent/`.

Expected result: either the downstream function yields a legitimate writer
and complete order join, or its destination remains unmapped. Do not promote
an address overlap into a mitigation or contract change.
