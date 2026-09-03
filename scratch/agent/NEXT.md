# NEXT work unit — initSaveData $s2 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3652 closed `freeRenderSubsystemResources`
`*0x8011A444` and its four sibling globals
as Complete. `funcs_4.c` original
`jal 0x80001C98` is exhausted; `funcs_3.c`,
`funcs_5.c`, and `funcs_0.c` have zero
sites. The live M3 unit is the first
remaining original `jal 0x80001C98` in
`funcs_2.c`.

Next work unit: perform one complete static census of
`initSaveData` `jal rs_free` at `0x8000671C`
(`$a0` = `$s2` from `addu $a0, $s2` at
`0x80006708`). Enumerate every original
load/store of that `$s2` (including the
matching allocator if any, every later
store, whether the caller holds the buffer,
and the sibling `jal rs_free` at
`0x8000672C` of the same `$s2`) and every
`jal rs_free` that can receive that
pointer. Include `freeSaveDataBuffer`
`0x80006774` (`$a0` = `*0x80112724`,
`lui 0x8011; lw 0x2724`) if that word is
the published `$s2`. Classify other loads
as consumers or as a second free.
Do not repeat the closed classes archived
in PROJECT-OVERVIEW §56 (s3586–s3652
Complete/Unevaluable families through
`freeRenderSubsystemResources`, plus the
s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
`$s2`.

If this census closes that site, continue
with any remaining sibling in
`initSaveData` / `freeSaveDataBuffer` that
were not covered, then the next remaining
original `jal 0x80001C98` in `funcs_2.c`
(`unregisterServiceWorker` `0x80007128`,
`$a0` = `$s0`).

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Discriminator: the single complete original census of that
`jal rs_free` site plus every original `lw`/`sw`/`addu` of
`initSaveData` `$s2` that can become this `$a0`, and every
`jal rs_free` that can receive that pointer. Include any
overlay duplicate of `initSaveData` / `0x80006338` if it is a
second generated body of the same PCs. Select Gap only with a
concrete non-allocator or already-freed edge; select Complete
only when all remaining edges are covered; otherwise select
Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_2.c
    grep -n -- 'initSaveData\|0x80006338\|0x8000671C' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x2724\|0x80112724' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
