# NEXT work unit (s2746) — audit the streaming-voice consumer boundary

HYPOTHESIS-ID: m5-mort-pcm-publication

## Work unit

Perform one bounded static audit of `serviceStreamingVoice` at `0x8009BF14`
and its immediate named caller/consumers. It must not repeat the renderer,
synth, command-list, allocation, host-AI, queue, PI-service, or
`serviceVoicePoolFrame` surfaces already closed. Do not add runtime
instrumentation or a writeback/remap.

## Competing hypotheses and discriminator

- H-stream-edge-found: the routine names a complete source, destination,
  ownership, and ordering edge from voice/MORT output to the AI source span.
- H-stream-edge-partial: it names a candidate stream handoff, but source,
  destination, ownership, or ordering remains unproven.
- H-stream-edge-absent: it only advances/reaps streamed voice state and has no
  relation to renderer/synth output or the AI source span.

The discriminator is a complete source/destination/ownership/order table for
the routine, its named caller, and immediate consumers. Each possible result
selects a full edge, a partial edge, or no edge. Static evidence alone does
not establish retail legitimacy or payload polarity.

## Exact commands

Session 2745 ruled out `serviceVoicePoolFrame` at `0x8009B5A8`: it services
four slot records, starts/reaps streamed voices, and signals a zero-token
cadence queue, with no MORT/renderer/AI publication edge. Use the generated
snapshot and companion symbols to classify every read, write, call, and
immediate caller/consumer of `serviceStreamingVoice`. Write the complete table
before any build or run; no runtime probe is justified unless this audit names
a legitimate destination and ordering edge.
