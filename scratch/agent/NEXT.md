# NEXT work unit (s2677) — audit the downstream MORT voice consumer

HYPOTHESIS-ID: m5-audio-cpu-mort-publication-boundary

## Work unit

Perform one bounded source audit of the next named downstream voice consumer
after `filterVoiceSampleBlock`/`applyVoiceDelayFilter`: identify its caller,
persistent input/output structure, and one source-derived destination. Then
ask the retail oracle about that destination with the whole-RDRAM control.
Do not change runtime behavior, add writeback, or repeat the task-field,
ring-destination, or shared-stack census.

## Competing hypotheses and discriminator

- `H-MORT-edge`: the downstream consumer has a persistent destination and a
  target-phase writer/order relation to PCM.
- `H-image-edge`: the downstream relation is absent, while the Factor 5 image
  has the complete consumer join.
- `H-MORT-unmapped`: the downstream value remains temporary/shared or lacks a
  legitimate payload/order join.

The discriminator is one table covering caller/entry, source-derived
destination, payload polarity, descriptor/type, target-phase writer rows,
port source/consumer event, image completion event, and ordering. A complete
CPU join selects `H-MORT-edge`; a complete image join selects `H-image-edge`;
a missing writer or ordering edge selects `H-MORT-unmapped`. The oracle
whole-RDRAM watch must fire first as the positive control.

## Exact commands

1. Use bounded `rg`/`sed` reads of the companion mapping/generated source for
   `filterVoiceSampleBlock`, `applyVoiceDelayFilter`, their callers, and the
   next named consumer.
2. Inspect `tools/oracle/README.md` and select the smallest source-derived
   `--watch-write` plus any needed `--watch-pc`; ask ground truth before adding
   port instrumentation.
3. Run one batched oracle capture only if it arms the whole-RDRAM positive
   control and target phase. A null without both controls is unevaluable.

Expected: the positive control remains live. Either the live function yields a
source-derived writer and complete order join, or its destination remains
unmapped. Do not promote a mitigation from address overlap.
