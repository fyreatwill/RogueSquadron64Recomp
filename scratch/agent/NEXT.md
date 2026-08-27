# NEXT work unit (s2751) — identify a new M5 publication surface

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

The previous audit closed the streaming callback edge: the indirect target at
`0x8009C040` is descriptor `+0x190`, initialized to fixed
`dmaVoiceSampleAndSignal` (`0x8009BE08`); `+0x194` is the sample source. Select
one new, source-backed CPU-side MORT publication surface from the remaining
named call/data graph. Do not repeat the streaming body, callback, queue,
renderer, mixer, AI-worker, PI-service, host-AI, or voice-pool audits. Do not
add a runtime watch until a legitimate AI destination and ordering edge are
named.

## Competing hypotheses and discriminator

- H-new-publisher: the selected surface contains a legitimate write into the
  AI-visible source span, with a named producer and ordering edge.
- H-service-only: the selected surface contains only state, DMA, timing, or
  queue work and cannot publish AI payload.
- H-unresolved: the selected surface remains data-driven or lacks a complete
  writer-to-destination chain.

The discriminator is a complete writer-to-target/dataflow table for the newly
selected surface. An explicit payload-to-AI and ordering edge selects
H-new-publisher; only service work selects H-service-only; an incomplete chain
selects H-unresolved. If no source-backed surface can be selected, stop and
switch to the ready generated-symbol renaming fallback rather than adding
instrumentation.

## Exact commands

1. Grep the named M5 call/data graph and `docs/M5-AUDIO-PLAN.md` for the next
   unclosed CPU-side producer; exclude the surfaces listed above.
2. Read only bounded windows around the selected writer, target, and consumer.
3. Record the complete table in a new `scratch/agent/s2751_*/audit.md` file;
   do not build or run unless a legitimate destination/order is identified.
