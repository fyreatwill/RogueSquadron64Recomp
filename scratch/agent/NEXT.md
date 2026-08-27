# NEXT work unit (s2692) — audit musyx-render callers and post-call consumers

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit of every direct named caller of
`musyxRenderVoiceSamples` and the immediate named consumers of its voice
object fields after the call. Record caller inputs, fields written by the
render routine, direct copies/transforms, queue or service signals, and any
ordering relation toward the AI source. Follow only named calls and direct
stores/copies; stop at unresolved indirect state. Do not repeat the
initializer, setup, renderer, mixer, filter, persistent-object, task-field,
shared-stack, DMA-callback, update/renderer, acquire, AI-submit, or ring-setup
body audits.

## Competing hypotheses and discriminator

- `H-render-publisher`: a render caller or its immediate consumer copies a
  legitimate rendered/MORT-derived payload toward the AI source or signals
  its publication.
- `H-service-boundary`: the render path is a named service boundary, but the
  payload source or AI relation remains outside the audited caller.
- `H-unresolved-address`: callers only manage voice state/fields or end at
  unresolved indirect pointers.

The discriminator is a complete caller/source/destination/order table. Each
outcome must identify the writer and legitimate payload polarity, or explicitly
show which field is absent. No runtime watch or build is allowed unless that
table names a ground-truth target and the whole-RDRAM positive control is
planned in the same run.

## Exact commands

1. `rg -n -H 'musyxRenderVoiceSamples|0x8008FFAC|0x80090B68|0x8009C240|0x801496' ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows for each unique named caller and immediate post-call
   consumer; follow only named calls or direct stores/copies.
3. Record the complete caller/source/destination/order table and selected
   hypothesis in the ledger/current truth; do not add runtime instrumentation
   from a static unresolved result.
