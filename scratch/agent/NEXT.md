# NEXT work unit (s2617) — audit port PCM writer/copy edges

HYPOTHESIS-ID: m5-port-publication-edge

## Single work unit

Perform one bounded static census of port-side direct stores, copies, and DMA
consumers that can publish the image task's PCM spans corresponding to retail
writers `0x800078EC`, `0x80007670`, `0x8001E2C0`, and
`0x8001FAxx–0x8001FD2C`. Add one regeneration-safe phase-gated witness only
if the census identifies a complete candidate edge. Do not change C88,
routing, dispatch, or output behavior.

## Competing hypotheses and discriminator

- `H-PortWriterIdentified`: a complete port store/copy edge reaches a retail-
  corresponding destination and can be witnessed without guessing a remap.
- `H-PortPublicationGap`: the port has no complete candidate edge at the
  retail spans, or only zero-valued host DMA/readback rows; the missing edge
  remains unresolved.
- `H-NonPCMWriter`: the candidate writers touch the spans for another valid
  purpose, while PCM is published elsewhere; destination/value joins reject
  treating them as audio output.

The discriminator is one table for every candidate edge: source function/PC,
destination physical span, length, value/hash/nonzero count, phase, and
ordering against image DMA, PCM source/consumer, and the independent retail
writer PCs. A complete matching edge selects `H-PortWriterIdentified`; no
candidate selects `H-PortPublicationGap`; a matching span with a non-audio
value/use selects `H-NonPCMWriter`.

## Exact checks

1. Search the generated/fixup/source trees for writes and copies covering
   physical `0x166450:0x169450` and `0x1798B0:0x179A48`, then inspect each
   complete caller/callee span and its existing task/PCM hooks. Use bounded
   `rg`/`sed` windows; do not read generated files wholesale.
2. Ask the retail oracle ground truth only if a new narrow witness is needed;
   its existing whole-RDRAM control must fire first. Batch all candidate edges
   in one build and one title/hangar phase-gated run, with positive controls
   for image DMA and PCM endpoints.

## Expected outcomes

- Complete candidate: add only its regeneration-safe witness and queue the
  validation soak; do not add writeback or remapping.
- No complete candidate: record the whole census and leave behavior unchanged;
  pivot to the next bounded M5 contract edge.
