# NEXT work unit (s2672) — audit the named M5 output/publication edge

HYPOTHESIS-ID: m5-audio-step3-output-publication-audit

## Work unit

Perform one bounded, static contract-edge audit using the qualified s2671
artifacts and the existing retail writer evidence. Trace the image arm's
phase-keyed DMA destinations and zero payloads through the known CPU MORT/PCM
source-consumer call chain, and identify whether `data_ptr+0x100`, an output
field, or a CPU writer is the next legitimate publication edge. Do not build,
change runtime behavior, add writeback, alter gates, or remove guards.

## Competing hypotheses and discriminator

- `H-image-contract-edge`: the image task's existing `data_ptr+0x100`/DMA
  relation names a legitimate port publication edge and its destination/order
  can be joined to PCM consumption.
- `H-cpu-mort-edge`: the missing nonzero PCM is produced by a CPU-side MORT
  writer after task completion, independent of the image DMA destinations.
- `H-unmapped-edge`: neither path can be joined to a named writer, legitimate
  destination/value, and completion-to-consumer order from current evidence.

The discriminator is one table, for every observed s2671 image DMA range and
PCM source/consumer row: task ordinal and phase, destination span, payload
nonzero/hash, candidate writer/function, MORT descriptor/type, and ordering
relative to image completion and consumer. A complete named image join selects
`H-image-contract-edge`; a complete CPU writer join selects `H-cpu-mort-edge`;
otherwise `H-unmapped-edge`. A missing positive-control row makes the audit
unevaluable rather than a null result.

## Exact commands

1. `rg -n "data_ptr|0x100|pcm-boundary|MORT|mort|audtask-(dma|image-stage)|pcm-(source|consumer)" src patches tools docs scratch/agent/s2671_m5_step1_contract_rebaseline`
2. Inspect bounded windows around the matched generated/fixup callsites and
   `tail -50` of the s2671 arm logs; write the table to a new scratch audit.

Expected: the s2671 positive controls remain valid, image DMA/image-stage work
is present, and the audit either names one complete publication edge or keeps
the edge explicitly unmapped without changing behavior.
