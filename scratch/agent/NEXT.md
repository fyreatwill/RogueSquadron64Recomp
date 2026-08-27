# NEXT work unit (s2695) — audit post-mix output-block handoff

HYPOTHESIS-ID: m5-mort-publication-postmix-boundary

## Work unit

Audit named/indirect consumers after `musyxMixActiveVoices` returns and the
`musyxSynthFrame` output-block handoff. Do not repeat the already-audited
initializer, setup, renderer, mixer, AI-submit, cache, acquire, or direct
caller bodies. Trace whether the per-frame output block passed as `$a3` at
`0x80090F00` is copied/transformed into the AI source, including writer,
destination, payload legitimacy, queue/service signal, and ordering relative
to `osAiSetNextBuffer`.

## Competing hypotheses and discriminator

- `H-postmix-publishes`: a named post-mix consumer copies the per-frame block
  into the AI-source span and orders the copy before submission.
- `H-consumer-only`: post-mix consumers only advance cursors/state; publication
  is in an unnamed or indirect helper outside the audited call graph.
- `H-service-boundary`: the output block is handed to a queue/callback whose
  consumer performs publication asynchronously.

The discriminator is a complete post-mix consumer table: every named or
indirect handoff, each output-block read/write, any payload copy/transform and
destination, queue/service signal, and ordering edge to AI submission. A
named legitimate copy selects `H-postmix-publishes`; state-only consumers
select `H-consumer-only`; a queued handoff selects `H-service-boundary`. If no
named edge exists, retain `H-unresolved-address` and do not add runtime
watches or writeback.

## Exact commands

1. Locate generated/fixup definitions, output-block arguments, post-mix calls,
   and AI submission with `rg -n "musyxMixActiveVoices|musyxSynthFrame|0x80090F00|0x801496B0|osAiSetNextBuffer"`.
2. Read bounded windows around each post-mix handoff and immediate consumer;
   record the complete table in
   `scratch/agent/s2695_mort_postmix_boundary/audit.md`.
3. Do not build or run unless the static table identifies a concrete runtime
   discriminator; no mitigation, writeback, remap, or watch is authorized by
   this unit.
