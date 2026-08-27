# NEXT work unit (s2697) — audit the next unresolved DMA-service consumer

HYPOTHESIS-ID: m5-mort-publication-postmix-boundary

## Work unit

Source-read the next unresolved consumer of the DMA-service callback resolved
at `0x80091670`/`0x80091684`: `sendServiceMessage` and the PI/DMA worker path
used by `submitDmaRequestBatch` (`0x8000569C`). Do not repeat the completed
renderer, mixer, post-mix maintenance, AI-submit, cache, acquire, or direct-
caller bodies. Trace whether this service handoff can carry the per-frame
output block into the AI source, including writer, destination, payload
legitimacy, queue/service signal, and ordering relative to `osAiSetNextBuffer`.

## Competing hypotheses and discriminator

- `H-service-publishes`: the DMA service consumer receives a legitimate audio
  payload and publishes it into the AI source.
- `H-service-indirect`: the service handoff reaches another named/indirect
  consumer that performs the publication asynchronously.
- `H-service-unrelated`: the service path only handles generic DMA descriptors
  and does not touch the synth output or AI source.

The discriminator is a complete service-consumer table: all request fields,
queue destinations, output-block reads/writes, payload copy/transform and
destination, service signal, and ordering edge to `osAiSetNextBuffer`. A named
legitimate copy selects `H-service-publishes`; a downstream publication
consumer selects `H-service-indirect`; a descriptor-only path selects
`H-service-unrelated` and retains `H-unresolved-address`. If the target remains
unresolved, record that limitation and do not add a runtime watch, writeback,
remap, or mitigation.

## Exact commands

1. Locate the service path:
   `rg -n "sendServiceMessage|submitDmaRequestBatch|0x801112B0|0x801126B[04]" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files`
2. Read bounded windows around `sendServiceMessage`, the PI/DMA worker, and
   their immediate consumers. Record the complete table in
   `scratch/agent/s2697_mort_dma_service_boundary/audit.md`.
3. Do not build or run unless the static table identifies a concrete runtime
   discriminator with a named destination and ordering edge.
