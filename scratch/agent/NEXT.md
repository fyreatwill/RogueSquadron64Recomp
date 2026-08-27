# NEXT work unit (s2699) — audit named post-mix stream consumers

HYPOTHESIS-ID: m5-mort-publication-cpu-consumer-chain

## Work unit

Source-read the implementations and direct callers/consumers of
`flushStreamedVoiceBuffers` and `serviceStreamedVoices`, plus the concrete
`copyFourHalfwordsWriteback` call chain named by s2695. Establish whether
either stream path receives the per-frame synth output pointer, copies a
legitimate payload into the AI worker's `0x801496B0` allocation, signals a
service/slot edge, or is unrelated bookkeeping. Do not repeat the already
audited renderer, mixer, DMA-service, or host-AI bodies.

## Competing hypotheses and discriminator

- `H-stream-publishes`: a named stream consumer receives or derives the synth
  output and publishes it into the AI source with ordering.
- `H-stream-relays`: a stream consumer forwards the output through an
  unresolved callback or descriptor whose next edge is the discriminator.
- `H-stream-unrelated`: the named stream functions only reap/clear descriptors
  or update cursors, with no payload or AI-source relation.

The discriminator is a complete source-level table for every direct caller and
immediate consumer: input/output pointers, payload copy or transform,
destination, queue/service signal, and relation to `0x801496B0` and
`osAiSetNextBuffer`. A named legitimate destination and ordering selects
`H-stream-publishes`; a concrete unresolved relay selects `H-stream-relays`;
absence of both selects `H-stream-unrelated`. No runtime watch, writeback,
remap, or mitigation is authorized unless the table names a legitimate writer
and destination.

## Exact commands

1. Locate all named stream symbols and address references:
   `rg -n "flushStreamedVoiceBuffers|serviceStreamedVoices|copyFourHalfwordsWriteback|0x801496B0|musyxSynthFrame" RecompiledFuncs docs scratch`
2. Read bounded windows around each implementation, direct caller, and
   immediate consumer; write the complete table to
   `scratch/agent/s2699_mort_stream_consumers/audit.md`.
3. Do not build or run unless the table identifies a concrete runtime
   discriminator and a positive-control-compatible phase.
