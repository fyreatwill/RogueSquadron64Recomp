# NEXT work unit (s2698) — audit the host AI queue boundary

HYPOTHESIS-ID: m5-mort-publication-host-ai-boundary

## Work unit

Source-read `ultramodern::queue_audio_buffer` and its immediate audio-consumer
path. Establish whether `osAiSetNextBuffer_recomp` preserves the game-supplied
RDRAM pointer/length, copies or transforms payload, substitutes another host
buffer, and how completion ordering relates to the AI worker's submitted
buffers. Do not repeat the completed game-side renderer, mixer, DMA-service,
cache, or AI-worker bodies.

## Competing hypotheses and discriminator

- `H-host-preserves`: the host queue consumes the exact game-supplied RDRAM
  span; the missing edge is upstream of the host boundary.
- `H-host-remaps`: the host queue copies/transforms into a different host or
  RDRAM destination, providing the missing publication edge.
- `H-host-gates`: host queueing/completion drops or defers the supplied span in
  a way that explains the zero payload observed by the port.

The discriminator is a complete host-AI table: input pointer/length,
RDRAM-to-host conversion, copy/transform destination, queue ownership,
consumer thread, completion signal, and ordering relative to
`osAiSetNextBuffer_recomp`. Exact pointer preservation selects
`H-host-preserves`; a named legitimate copy selects `H-host-remaps`; a
drop/defer condition with evidence selects `H-host-gates`. If the host path is
only a transport wrapper, retain the upstream unresolved edge and add no
runtime watch, writeback, remap, or mitigation.

## Exact commands

1. Locate the queue and consumers:
   `rg -n "queue_audio_buffer|get_remaining_audio_bytes|audio_buffer|audio queue|set_audio_frequency" lib/N64ModernRuntime/ultramodern lib/N64ModernRuntime/librecomp src`
2. Read bounded windows around the queue implementation, its consumer thread,
   and `osAiSetNextBuffer_recomp`; record the complete table in
   `scratch/agent/s2698_mort_host_ai_boundary/audit.md`.
3. Do not build or run unless the table identifies a concrete runtime
   discriminator and a positive-control-compatible phase.
