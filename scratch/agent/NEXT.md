# NEXT work unit (s2745) — audit the voice-pool service boundary

HYPOTHESIS-ID: m5-mort-pcm-publication

## Work unit

Perform one bounded static audit of `serviceVoicePoolFrame` at `0x8009B5A8`
and its immediate named caller/consumers. It must not repeat the renderer,
synth, command-list, streamed-voice, allocation, host-AI, queue, or PI-service
surfaces already closed. Do not add runtime instrumentation or a
writeback/remap.

## Competing hypotheses and discriminator

- H-service-edge-found: the service names a complete source, destination,
  ownership, and ordering edge from voice/MORT output to the AI source span.
- H-service-edge-partial: it names a candidate handoff, but source,
  destination, ownership, or ordering remains unproven.
- H-service-edge-absent: it only services voice state/slots and has no relation
  to renderer/synth output or the AI source span.

The discriminator is a complete source/destination/ownership/order table for
the service routine, its named caller, and immediate consumers. Each possible
result identifies a full edge, a partial edge, or no edge. This is static
evidence only; no runtime legitimacy or payload conclusion follows without the
retail oracle.

## Exact commands

Session 2744 ruled out `musyxBuildVoiceCommandList` at `0x80091034`: it only
builds a rotating `0x30`-byte command-descriptor list from voice/control state;
there is no sample copy, AI-span access, PCM call, or publication ordering.
Use the generated snapshot and companion symbols to classify every read,
write, call, and immediate caller/consumer of `serviceVoicePoolFrame`. Write
the complete table before any build or run; no runtime probe is justified
unless this audit names a legitimate destination and ordering edge.
