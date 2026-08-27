# NEXT work unit (s2743) — identify one new opaque M5 publication boundary

HYPOTHESIS-ID: m5-mort-pcm-publication

## Work unit

Perform one bounded static audit of exactly one newly named opaque or
data-driven M5 boundary that could connect the renderer/synth output to the
AI source span. It must not repeat the renderer, synth, streamed-voice,
allocation, host-AI, queue, or PI-service surfaces closed by s2742. Do not add
runtime instrumentation or a writeback/remap.

## Competing hypotheses and discriminator

- H-opaque-edge-found: the new boundary names a complete source, destination,
  ownership, and ordering edge.
- H-opaque-edge-partial: it names a candidate handoff, but source,
  destination, ownership, or ordering remains unproven.
- H-opaque-edge-absent: the new boundary has no relation to renderer/synth
  output or the AI source span; move to the next independently named surface.

The discriminator is a complete source/destination/order table for the new
boundary. Each possible result identifies a full edge, a partial edge, or no
edge. This is static evidence only; no runtime legitimacy or payload
conclusion follows without the retail oracle.

## Exact commands

First locate one genuinely new indirect/data-driven caller or destination
with bounded searches, then record all competing outcomes in `NEXT.md` before
any build or run. The previous audit evidence is
`scratch/agent/s2742_mort_publication_audit.md`.
