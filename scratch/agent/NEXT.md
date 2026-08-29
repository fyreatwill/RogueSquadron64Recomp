# NEXT work unit — bounded MusyX pointer-class guard audit

HYPOTHESIS-ID: m3-musyx-pointer-class-audit

Session 3237 selected a new repeated M3 class: unguarded MusyX pointer globals
`0x80149758` (`-0x68A8`) and `0x80149750` (`-0x68B0`). The census did not
authorize a guard; exact site recovery and writer/free ordering are next.

## Competing hypotheses

- `H-LegitimatePublished`: allocator/build writers publish valid KSEG0 pointers
  before every consumer and no guard is needed.
- `H-UnresolvedConsumer`: at least one reader can consume an invalid or stale
  pointer and needs a patch-based guard audit.
- `H-NonAudioAlias`: out-of-region callers are unrelated aliases and must be
  split from the MusyX class.

## Discriminator

Recover the exact function/address for every `-0x68A8` and `-0x68B0` site in
the generated tree, then grep all fixup rules for those sites. Enumerate
writers, frees, aliases, and consumer dereferences; classify every site as
guarded, proven in-range, or unresolved. Complete writer/free/order proof
selects `H-LegitimatePublished`; one unresolved consumer selects
`H-UnresolvedConsumer`; unrelated non-MusyX callers select `H-NonAudioAlias`.
If a guard is selected, land it through `patches/` with an `ORIGIN:` line.

## Exact commands

1. `rg -n -- "-0X68A8|-0X68B0" ../N64Recomp/RecompiledFuncs/funcs_*.c`
2. Recover exact function headers and bounded windows for every site; inspect
   `tools/fixup*` for matching transformations.
3. Enumerate writers/free edges and classify every site in a new
   `scratch/agent/s3238_m3_*` report. Build only if the audit selects a
   concrete patch-based guard; otherwise do not run the game.
