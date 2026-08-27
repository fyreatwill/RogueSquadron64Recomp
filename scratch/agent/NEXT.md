# NEXT work unit (s2675) — audit the CPU-side MORT publication boundary

HYPOTHESIS-ID: m5-audio-cpu-mort-publication-boundary

## Work unit

Perform one bounded source-and-ground-truth audit of the CPU-side MORT voice
publication boundary. Start from the named MORT/voice callsites and exact
retail PCs already identified in `docs/PROJECT-OVERVIEW.md`, then choose one
new oracle watch that can attribute a specific source/destination write or
callsite to the target phase. Do not change runtime behavior, add writeback,
or repeat the task-field/ring-destination census.

## Competing hypotheses and discriminator

- `H-MORT-edge`: a named CPU-side MORT/voice callsite has a legitimate source,
  destination, and target-phase order that can be joined to PCM consumption.
- `H-image-edge`: the apparent CPU-side boundary is actually the Factor 5
  image contract, with a complete image-to-consumer join.
- `H-MORT-unmapped`: neither source provides a legitimate MORT publication
  edge with destination, payload polarity, and order.

The discriminator is one table covering each named MORT callsite: retail PC,
watched source/destination, value/payload polarity, descriptor/type, port
source/consumer event, image completion event, and ordering. A complete CPU
join selects `H-MORT-edge`; a complete image join selects `H-image-edge`; any
missing writer or ordering edge selects `H-MORT-unmapped`. The oracle
whole-RDRAM watch must fire first as the positive control.

## Exact commands

1. Use `rg -n "MORT|mort|voice|filterVoice|startVoice|queue_samples|pcm" src
   docs/PROJECT-OVERVIEW.md docs/game-architecture.md
   scratch/agent/s2673_m5_ring_writer_ground_truth.md` and read bounded
   windows.
2. Inspect `tools/oracle/README.md` for the smallest new `--watch-pc` or
   `--watch-write` that can attribute one named MORT edge; ask ground truth
   before adding any new port instrumentation.
3. Run one batched oracle/port capture only if the oracle can arm the
   whole-RDRAM positive control and target phase; otherwise record the
   limitation without interpreting a narrow null.

Expected: the positive control remains live. Either a named independent writer
and complete order join closes one ring hypothesis, or the ring remains
explicitly unmapped. Do not promote a mitigation from address overlap.
