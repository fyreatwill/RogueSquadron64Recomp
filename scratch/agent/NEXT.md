# NEXT work unit — teardownAssetManifestService *0x80110D50 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3657 closed `freeManifestSegmentAssets`
`0x40($s0)` at `0x80004A0C` /
`0x80004A80` as Complete. That word is
the DMA-slot payload malloc stored at
`0x80004920`. The live M3 unit is the
next remaining original `jal 0x80001C98`
in `funcs_1.c`.

Next work unit: perform one complete static census of
`teardownAssetManifestService` `jal rs_free` at
`0x80005000` (`$a0` = `*0x80110D50` from
`lw $a0, 0xD50($v0)` at `0x80004FF4`,
after `beq $a0, $zero` skip).
Enumerate every original load/store of
that `*0x80110D50` (including the matching
allocator `initDmaSlots` `rs_malloc`
store at `0x80004708`, every later store,
whether the caller holds the buffer, the
NULL skip at `0x80004FF8`, and any sibling
`jal rs_free` of the same pointer or of
adjacent `0xD48`/`0xD4C`/`0xD54` words)
and every `jal rs_free` that can
receive that pointer. Classify other
loads as consumers or as a second free.
Do not repeat the closed classes
archived in PROJECT-OVERVIEW §56
(s3586–s3657 Complete/Unevaluable
families through `freeManifestSegmentAssets`
`0x40($s0)`, plus the s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
`*0x80110D50`.

If this census closes that site, continue
with the next remaining original
`jal 0x80001C98` in `funcs_1.c`
(`rs_zcfree` `0x80005268`).

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
`jal rs_free` site plus every original `lw`/`sw`/`addu`
of `teardownAssetManifestService` `*0x80110D50` that can become
this `$a0`, every original `lw`/`sw` of the same word,
and every `jal rs_free` that can receive that pointer. Include
any overlay duplicate of `teardownAssetManifestService` /
`0x80004FD8` if it is a second generated body of the same PCs.
Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are
covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_1.c
    grep -n -- 'teardownAssetManifestService\|0x80004FD8\|0x80005000\|0xD50' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- 'sw          \$v0, 0xD50\|lw          \$a0, 0xD50' ../N64Recomp/RecompiledFuncs/funcs_1.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
