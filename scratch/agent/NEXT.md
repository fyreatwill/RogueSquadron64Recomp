# NEXT work unit (s2676) — audit the live MORT voice-boundary destination

HYPOTHESIS-ID: m5-audio-cpu-mort-publication-boundary

## Work unit

Perform one bounded source audit of the live `0x8009D740` voice boundary,
identified in s2675 as `updateVoiceChannelParamsLarge` with caller
`0x8009D73C`. Trace its stores and destination structure from the companion
mapping/generated source, then choose one new oracle watch on that
source-derived destination. Do not change runtime behavior, add writeback, or
repeat the task-field/ring-destination census.

## Competing hypotheses and discriminator

- `H-MORT-edge`: the live `0x8009D740` boundary has a legitimate source,
  destination, and target-phase order that can be joined to PCM consumption.
- `H-image-edge`: the apparent CPU-side boundary is actually the Factor 5
  image contract, with a complete image-to-consumer join.
- `H-MORT-unmapped`: neither source provides a legitimate MORT publication
  edge with destination, payload polarity, and order.

The discriminator is one table covering the live function: caller/entry,
source-derived destination, payload polarity, descriptor/type, target-phase
writer rows, port source/consumer event, image completion event, and ordering.
A complete CPU join selects `H-MORT-edge`; a complete image join selects
`H-image-edge`; a missing writer or ordering edge selects `H-MORT-unmapped`.
The oracle whole-RDRAM watch must fire first as the positive control.

## Exact commands

1. Use bounded `rg`/`sed` reads of the companion mapping/generated source for
   `0x8009D740`, its caller, and every store in the function.
2. Inspect `tools/oracle/README.md` and select the smallest source-derived
   `--watch-write` plus any needed `--watch-pc`; ask ground truth before adding
   port instrumentation.
3. Run one batched oracle capture only if it arms the whole-RDRAM positive
   control and target phase. A null without both controls is unevaluable.

Expected: the positive control remains live. Either the live function yields a
source-derived writer and complete order join, or its destination remains
unmapped. Do not promote a mitigation from address overlap.
