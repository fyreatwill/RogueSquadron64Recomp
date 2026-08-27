# NEXT work unit (s2691) — audit acquire-sample callers and post-acquire consumers

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit of every direct named caller of
`acquireSampleStreamBlock` and the immediate named consumers of its return
value. Record the caller's source argument, the returned block's destination
fields, any copy/transform, queue or service signal, and ordering relation.
Follow only named calls and direct stores/copies; stop at unresolved indirect
state. Do not repeat the initializer, setup, renderer, mixer, filter,
persistent-object, task-field, shared-stack, DMA-callback, update/renderer,
AI-submit, or ring-setup body audits.

## Competing hypotheses and discriminator

- `H-acquire-publisher`: an acquire caller or its immediate consumer copies a
  legitimate stream/MORT-derived payload toward the AI source or signals its
  publication.
- `H-service-boundary`: the cache path is a named service boundary, but the
  payload source or AI relation remains outside the audited caller.
- `H-unresolved-address`: callers only manage block ownership/fields or end at
  unresolved indirect pointers.

The discriminator is a complete caller/source/destination/order table. Each
outcome must identify the writer and legitimate payload polarity, or explicitly
show which field is absent. No runtime watch or build is allowed unless that
table names a ground-truth target and the whole-RDRAM positive control is
planned in the same run.

## Exact commands

1. `rg -n -H 'acquireSampleStreamBlock|0x8008F758|0x80091944|0x801499|0x801496' ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows for each unique caller and immediate named consumer;
   follow only named calls or direct stores/copies.
3. Record the complete caller/source/destination/order table and selected
   hypothesis in the ledger/current truth; do not add runtime instrumentation
   from a static unresolved result.
