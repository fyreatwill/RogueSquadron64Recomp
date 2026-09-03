# NEXT work unit — destroyTextureLUTs *0x80128F08 / *0x80128EFC rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3649 was a triggered maintenance compaction of CURRENT-TRUTH
(60,386 → 13,927 bytes; 1,020 → 227 lines). The live M3 unit is unchanged.

Next work unit: perform one complete static census of
`destroyTextureLUTs` `jal rs_free`
at `0x8001E344` (`$a0` = `*0x80128F08`) and
the sibling `jal rs_free` at `0x8001E354`
(`$a0` = `*0x80128EFC`). Enumerate
every original load/store of those two
words (including the matching
allocator stores, every later store, and
whether any caller holds the buffers) and
every `jal rs_free` that can receive those
pointers. Classify other loads as consumers
or as a second free.
Do not repeat the closed classes archived
in PROJECT-OVERVIEW §56 (s3586–s3648
Complete/Unevaluable families through
`loadDebugAssets` `$s0`, plus the s3636
Gap at `attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
word. Existing host TEXDATA_TABLE_GUARD /
TEXDATA_PTR_ARRAY_GUARD substitutions at
these two loads (s468/s470) are not this
work unit and must not be treated as an
original skip.

If this census closes both `destroyTextureLUTs`
sites, the following unit is
`uploadTextureDescriptorData` `$s1`
`rs_free` at `0x800232CC` (the last remaining
original `jal 0x80001C98` in `funcs_6.c`).

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Discriminator: the single complete original census of those
two `jal rs_free` sites plus every original `lw`/`sw`/`addu`
of `*0x80128F08` and `*0x80128EFC` that can become this
`$a0`, and every `jal rs_free` that can receive those
pointers. Include any overlay duplicate of
`destroyTextureLUTs` / `0x8001E334` if it is a second
generated body of the same PCs. Select Gap only with a
concrete non-allocator or already-freed edge; select
Complete only when all remaining edges are covered;
otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_6.c
    grep -n -- 'destroyTextureLUTs\|0x8001E334\|0x8001E344\|0x8001E354\|-0x70F8\|-0x7104' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x80128F08\|0x80128EFC' ../N64Recomp/RecompiledFuncs/funcs_*.c | head

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
