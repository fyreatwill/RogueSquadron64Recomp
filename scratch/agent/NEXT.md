# NEXT work unit — verify MusyX command-list allocation failure and teardown semantics

HYPOTHESIS-ID: m3-musyx-pointer-class-audit

Session 3238 split the repeated immediate class by effective address and
found the true MusyX chain unresolved because `rs_malloc` publication has no
success check and teardown does not visibly clear the published array. The
next unit is one bounded static failure/order audit; do not add a runtime
counter or build unless this audit identifies a concrete patch contract.

## Competing hypotheses

- `H-AllocatorNeverNull`: the heap allocator is fatal or otherwise guarantees
  a non-null result for these fixed-size audio allocations; the true consumers
  are legitimately published and no guard is needed.
- `H-NullConsumer`: `rs_malloc` can return zero and the indexed load/write
  sequence at `0x80091060` can dereference it; a patch guard has a concrete
  writer and failure contract.
- `H-TeardownStale`: either teardown free can race or be followed by a synth
  consumer because `0x80149758`/`0x80149750` are not cleared; the needed
  contract is ordering/clear publication, not an allocation guard.

## Discriminator

Recover the `rs_malloc` failure return path and all callers/order edges around
`allocateSongChannelArray`, `musyxSynthFrame`, `shutdownAudioEngine`, and
`waitForMusyXAudioTaskDone`. A fatal/non-returning failure path plus teardown
call exclusion selects `H-AllocatorNeverNull`; a returning zero reaching the
published array selects `H-NullConsumer`; a post-free or concurrent consumer
edge selects `H-TeardownStale`. If an actual guard or clear is selected, land
only through `patches/`, with an `ORIGIN:` naming the writer and whether the
value is legitimate.

## Exact commands

1. `rg -n -B8 -A35 "L_80001C74|jr.*ra|rs_malloc" ../N64Recomp/RecompiledFuncs/funcs_0.c`
   and identify the return value on every allocator failure branch.
2. `rg -n -B8 -A12 "allocateSongChannelArray|musyxSynthFrame|shutdownAudioEngine|waitForMusyXAudioTaskDone|8008F228|80091060|80091074|80091E28|80091F78" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/*.txt`
   and recover callers plus teardown ordering.
3. Write `scratch/agent/s3239_m3_musyx_pointer_order.md` with the selected
   hypothesis and the full writer/consumer/free table. Build only if a
   patch-based guard or ordering change is justified by the discriminator.
