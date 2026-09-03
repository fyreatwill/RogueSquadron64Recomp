# NEXT work unit — processAssetLoadStep 0x48($s0) rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3654 closed `unregisterServiceWorker` `$s0`
/ `*0x801128D0` as Complete. `funcs_2.c`
original `jal 0x80001C98` is exhausted;
`funcs_3.c`, `funcs_5.c`, and `funcs_0.c`
have zero sites. The live M3 unit is the
first remaining original `jal 0x80001C98`
in `funcs_1.c`.

Next work unit: perform one complete static census of
`processAssetLoadStep` `jal rs_free` at
`0x80003E7C` (`$a0` = `0x48($s0)` from
`lw $a0, 0x48($s0)` at `0x80003E78`).
Enumerate every original load/store of
that `0x48($s0)` (including the matching
allocator if any, every later store,
whether the caller holds the buffer, the
post-free `sw $zero, 0x48($s0)` at
`0x80003E8C`, and any sibling
`jal rs_free` of the same word or of
adjacent slots on `$s0`) and every
`jal rs_free` that can receive that
pointer. Classify other loads as
consumers or as a second free.
Do not repeat the closed classes archived
in PROJECT-OVERVIEW §56 (s3586–s3654
Complete/Unevaluable families through
`unregisterServiceWorker`, plus the s3636
Gap at `attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
`0x48($s0)`.

If this census closes that site, continue
with the next remaining original
`jal 0x80001C98` in `funcs_1.c`
(`0x8000450C`).

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
`processAssetLoadStep` `0x48($s0)` that can become this `$a0`,
and every `jal rs_free` that can receive that pointer. Include
any overlay duplicate of `processAssetLoadStep` /
`0x80003D64` if it is a second generated body of the same PCs.
Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are
covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_1.c
    grep -n -- 'processAssetLoadStep\|0x80003D64\|0x80003E7C' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x48(\$s0)\|0x48(\$s1)\|0x48(\$s2)' ../N64Recomp/RecompiledFuncs/funcs_1.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
