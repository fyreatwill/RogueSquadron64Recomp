# NEXT work unit — join port producer payload

HYPOTHESIS-ID: m5-port-producer-payload-join

Session 3414 established the independent retail destination: in the
512-wide `0x006AB400` hangar bucket, `0x800078EC` wrote the port source span
`0x1797B0:0x179A48` 664 times with nonzero post-store samples, and did not write
the alternate `0x1935E0` destination. The next unit must compare the port
producer's call/input/payload contract against that ground truth.

Competing hypotheses and discriminating measurement:

- H-PortProducerNonzero: port `0x800078EC` writes the hangar source span with
  nonzero payload matching the retail contract; the remaining zero PCM is
  downstream of this edge.
- H-PortProducerZero: port `0x800078EC` is phase-live but its source span is
  zero, selecting a producer-input or transform gap.
- H-PortProducerAbsent: port has no phase-qualified producer edge, selecting
  a dispatch/caller gap despite the retail destination match.

The single discriminator is one fresh-build port silent/image pair with the
existing phase, audio-task/ABI, image-stage, and PCM controls plus one batched
producer witness. Require title and hangar gates, both arm controls, and a
hangar source-span payload summary before classifying.

Exact commands:

1. Reuse the existing qualified port pair recipe (the M5 task/image/PCM
   controls) and add one phase-scoped witness for producer `0x800078EC` and
   physical span `0x1797B0:0x179A48`; build once with all counters enabled.
2. Run both silent and image arms from `build/`, then require title 1024,
   hangar 512, ABI/DMA, image-stage, and PCM controls before classifying the
   producer payload result.
