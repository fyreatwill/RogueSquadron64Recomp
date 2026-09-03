# NEXT work unit — freeRenderSubsystemResources *0x8011A444 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3651 closed `uploadTextureDescriptorData`
`$s1` as Complete. `funcs_6.c` original
`jal 0x80001C98` is exhausted; `funcs_5.c`
has zero sites. The live M3 unit is the
first remaining original `jal 0x80001C98`
in `funcs_4.c`.

Next work unit: perform one complete static census of
`freeRenderSubsystemResources` `jal rs_free`
at `0x80018668` (`$a0` = `*0x8011A444`,
`lui 0x8012; lw -0x5BBC`). Enumerate every
original load/store of that word (including
the matching allocator if any, every later
store, whether the caller holds the buffer,
and the four sibling `jal rs_free` in the
same wrapper at `0x80018680` / `0x80018698`
/ `0x800186A8` / `0x800186B8` of
`*0x801163B4`, `*0x801143AC`, `*0x8010E8A8`,
`*0x8010E8AC`) and every `jal rs_free` that
can receive those pointers. Classify other
loads as consumers or as a second free.
Do not repeat the closed classes archived
in PROJECT-OVERVIEW §56 (s3586–s3651
Complete/Unevaluable families through
`uploadTextureDescriptorData` `$s1`, plus
the s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
word. Host `MATERIAL_ARRAY_PTR_GUARD` at
`0x80018664` is not an original skip.

If this census closes that site, continue
with any remaining sibling globals in the
same wrapper that were not covered, then
the next remaining original `jal 0x80001C98`
in `funcs_4.c` (or the next lower numbered
file that still has one).

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
`*0x8011A444` that can become this `$a0`, and every
`jal rs_free` that can receive that pointer. Include any
overlay duplicate of `freeRenderSubsystemResources` /
`0x80018650` if it is a second generated body of the same
PCs. Select Gap only with a concrete non-allocator or
already-freed edge; select Complete only when all remaining
edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_4.c
    grep -n -- 'freeRenderSubsystemResources\|0x80018650\|0x80018668' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '-0x5BBC\|0x8011A444\|0x8012A444' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
