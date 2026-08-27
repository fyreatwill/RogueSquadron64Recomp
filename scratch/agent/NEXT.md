# NEXT work unit (s2679) — audit renderer-to-PCM publication

HYPOTHESIS-ID: m5-audio-cpu-mort-publication-boundary

## Work unit

Perform one bounded audit after `renderVoiceAudioBlock` /
`audioMixStereoBlock8`: identify the next named PCM/AI source and consumer,
their caller, persistent buffer, and one source-derived destination. Use the
existing port PCM boundary logs and ask the retail oracle about the matching
retail destination with the whole-RDRAM positive control and target phase. Do
not change runtime behavior, add writeback, or repeat filter, persistent-object,
task-field, image-ring, or shared-stack censuses.

## Competing hypotheses and discriminator

- `H-MORT-edge`: the renderer's persistent voice object reaches a legitimate
  PCM/AI source and consumer in order.
- `H-image-edge`: the CPU renderer-to-PCM edge is absent while the Factor 5
  image has a complete consumer join.
- `H-MORT-unmapped`: the renderer output remains temporary/shared or lacks a
  legitimate payload/order join.

The discriminator is one table covering renderer/mix caller, persistent input
and output destination, payload polarity, target-phase retail writer rows,
port PCM source/consumer events, image completion, and ordering. A complete
CPU-to-PCM join selects `H-MORT-edge`; a complete image join selects
`H-image-edge`; missing writer or ordering selects `H-MORT-unmapped`. A narrow
null is invalid unless the same oracle run visibly fires its whole-RDRAM
control and reaches the target phase.

## Exact commands

1. Use bounded `rg`/`sed` reads of companion mappings, generated source, and
   existing PCM boundary probes for `renderVoiceAudioBlock`,
   `audioMixStereoBlock8`, and AI calls.
2. Read `tools/oracle/README.md`; choose the smallest source-derived retail
   watch and needed `--watch-pc`. Ask ground truth before adding port
   instrumentation.
3. Run one batched oracle capture only after the positive-control and phase
   gates are armed. Record the table and artifact under `scratch/agent/`.

Expected result: either the renderer yields a legitimate PCM/AI writer and
complete order join, or its destination remains unmapped. Do not promote an
address overlap into a mitigation or contract change.
