# NEXT work unit (s2694) — audit MORT stream-render caller publication boundary

HYPOTHESIS-ID: m5-mort-publication-caller-boundary

## Work unit

Audit every named direct caller of `musyxRenderVoiceSamples` and immediate
consumers of its voice-object fields. Do not repeat the already-audited
initializer, setup, renderer, mixer, AI-submit, cache, or acquire bodies.
Trace source/cache-to-AI publication candidates: writer, destination, payload
legitimacy, queue/service signal, and ordering relative to
`osAiSetNextBuffer`.

## Competing hypotheses and discriminator

- `H-caller-publishes`: a named caller copies decoded/rendered payload into the
  AI-source span and orders the copy before submission.
- `H-consumer-only`: callers only advance cursors/state; publication is in an
  unnamed or indirect helper outside the audited call graph.
- `H-service-boundary`: a caller hands a buffer to a queue/callback whose
  consumer performs publication asynchronously.

The discriminator is a complete caller/consumer table: every direct caller,
each post-call field read/write, any payload copy/transform and destination,
queue/service signal, and ordering edge to AI submission. A named legitimate
copy selects `H-caller-publishes`; cursor/state-only callers select
`H-consumer-only`; a queued handoff selects `H-service-boundary`. If no named
edge exists, retain `H-unresolved-address` and do not add runtime watches or
writeback.

## Exact commands

1. Locate generated/fixup definitions and all direct callers with
   `rg -n "musyxRenderVoiceSamples|0x800902DC|0x80090B68"`.
2. Read bounded windows around each caller and immediate consumer; record the
   complete table in `scratch/agent/s2694_mort_caller_boundary/audit.md`.
3. Do not build or run unless the static table identifies a concrete runtime
   discriminator; no mitigation, writeback, remap, or watch is authorized by
   this unit.
