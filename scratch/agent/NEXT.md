# NEXT work unit (s2690) — audit the sample-stream cache boundary

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit of `initSampleStreamBlockCache` and every
direct named caller. Record each source, destination, copy/transform operation,
queue or service signal, and ordering relation. Follow only named calls and
direct stores/copies; stop at unresolved indirect state. Do not repeat the
renderer, mixer, filter, persistent-object, task-field, shared-stack,
DMA-callback, update/renderer, AI-submit, or ring-setup audits.

## Competing hypotheses and discriminator

- `H-cache-producer`: the cache path copies a legitimate rendered/MORT-derived
  payload toward the AI source or signals its publication.
- `H-service-boundary`: the cache path is a named service boundary, but the
  payload source or AI relation remains outside the audited caller.
- `H-unresolved-address`: the cache path only initializes/advances unrelated
  state or ends at unresolved indirect pointers.

The discriminator is a complete caller/source/destination/order table. Each
outcome must identify the writer and legitimate payload polarity, or explicitly
show which field is absent. No runtime watch or build is allowed unless that
table names a ground-truth target and the whole-RDRAM positive control is
planned in the same run.

## Exact commands

1. `rg -n -H 'initSampleStreamBlockCache|acquireSampleStreamBlock|sampleStreamBlock|0x801499|0x801496' ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows for each unique helper and direct named caller; follow
   only named calls or direct stores/copies.
3. Record the complete table and selected hypothesis in the ledger/current
   truth; do not add runtime instrumentation from a static unresolved result.
