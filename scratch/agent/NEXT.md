# NEXT work unit — uploadTextureDescriptorData $s1 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3650 closed `destroyTextureLUTs`
`*0x80128F08` / `*0x80128EFC` as Complete.
The live M3 unit is the last remaining
original `jal 0x80001C98` in `funcs_6.c`.

Next work unit: perform one complete static census of
`uploadTextureDescriptorData` `jal rs_free`
at `0x800232CC` (`$a0` = `$s1`, bound at
`0x800232A8` to incoming `$a1`). Enumerate
every original load/store of that `$s1`
(including the matching allocator if any,
every later store, whether the caller
`tickWrappingTimerAccumulatorList`
`0x8005477C` holds the buffer, and the
interior `$a1 = 0x0($s2) + (*(*s2+0xC) *
($s1&0xFFFF) + 0x14)` delay-slot address)
and every `jal rs_free` that can receive
that pointer. Classify other loads as
consumers or as a second free.
Do not repeat the closed classes archived
in PROJECT-OVERVIEW §56 (s3586–s3650
Complete/Unevaluable families through
`destroyTextureLUTs` `*0x80128F08` /
`*0x80128EFC`, plus the s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
`$s1`.

If this census closes that site,
`funcs_6.c` original `jal 0x80001C98` is
exhausted; the following unit is the next
remaining original `jal 0x80001C98` in
`funcs_5.c` (or the next lower numbered
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
`uploadTextureDescriptorData` `$s1` that can become this
`$a0`, and every `jal rs_free` that can receive that
pointer. Include any overlay duplicate of
`uploadTextureDescriptorData` / `0x80023274` if it is a second
generated body of the same PCs. Select Gap only with a
concrete non-allocator or already-freed edge; select
Complete only when all remaining edges are covered;
otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_6.c
    grep -n -- 'uploadTextureDescriptorData\|0x80023274\|0x800232CC' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- 'jal         0x80023274\|tickWrappingTimerAccumulatorList' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
