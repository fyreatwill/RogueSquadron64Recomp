# NEXT work unit — rs_zcfree incoming $a0 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3658 closed `teardownAssetManifestService`
`*0x80110D50` at `0x80005000` as Complete.
That word is the extra-heap flags-0x81 malloc
stored at `0x80004708`. The live M3 unit is
the last remaining original `jal 0x80001C98`
in `funcs_1.c`.

Next work unit: perform one complete static census of
`rs_zcfree` `jal rs_free` at `0x80005268`
(`$a0` = incoming `$a0` after `beq $a0, $zero`
skip at `0x80005260`). Enumerate every original
caller of `rs_zcfree` (`0x8000525C`) and of the
generated wrapper `zcfree` (`0x80029CF4`), every
load/store that can become that `$a0` (including
the matching `rs_zcalloc` / `rs_malloc` if any,
every later store, whether the caller holds the
buffer, the NULL skip, and any sibling `jal rs_free`
of the same pointer), and every `jal rs_free` that
can receive that pointer. Classify other loads as
consumers or as a second free.
Do not repeat the closed classes
archived in PROJECT-OVERVIEW §56
(s3586–s3658 Complete/Unevaluable
families through `teardownAssetManifestService`
`*0x80110D50`, plus the s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
incoming `$a0`.

If this census closes that site, `funcs_1.c`
`jal 0x80001C98` is exhausted. The next
remaining original site is then the first
still-open `jal 0x80001C98` outside the
closed files (`funcs_8.c` and above were
closed earlier; check `funcs_9.c` only if
a site remains after confirming
`funcs_1.c` is empty). Prefer the next
unclosed generated file with remaining
sites over re-auditing a Complete class.

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
of `rs_zcfree` incoming `$a0` that can become this `$a0`,
every original caller of `0x8000525C` / `0x80029CF4`,
and every `jal rs_free` that can receive that pointer.
Include any overlay duplicate of `rs_zcfree` /
`0x8000525C` if it is a second generated body of the same PCs.
Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are
covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_1.c
    grep -n -- 'rs_zcfree\|zcfree\|0x8000525C\|0x80005268' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- 'jal         0x8000525C\|jal         0x80029CF4' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
