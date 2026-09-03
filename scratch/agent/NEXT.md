# NEXT work unit — unregisterServiceWorker $s0 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3653 closed `initSaveData` `$s2`
and `freeSaveDataBuffer` `*0x80112724`
as Complete. `funcs_2.c` original
`jal 0x80001C98` has one remaining site;
`funcs_3.c`, `funcs_5.c`, and `funcs_0.c`
have zero sites. The live M3 unit is the
last remaining original `jal 0x80001C98`
in `funcs_2.c`.

Next work unit: perform one complete static census of
`unregisterServiceWorker` `jal rs_free` at
`0x80007128` (`$a0` = `$s0` from
`addu $a0, $s0` at `0x8000712C`).
Enumerate every original load/store of
that `$s0` (including the matching
allocator if any, the list-head word
`*0x801128D0` / `lui 0x8011; lw 0x28D0`,
every later store, whether the caller
holds the node, and any sibling
`jal rs_free` of the same node or of
`0x18($s0)` / `0x20($s0)`) and every
`jal rs_free` that can receive that
pointer. Classify other loads as
consumers or as a second free.
Do not repeat the closed classes archived
in PROJECT-OVERVIEW §56 (s3586–s3653
Complete/Unevaluable families through
`initSaveData` / `freeSaveDataBuffer`,
plus the s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
`$s0`.

If this census closes that site, continue
with the next remaining original
`jal 0x80001C98` in `funcs_1.c` (first
of seven: `0x80003E7C`).

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
`unregisterServiceWorker` `$s0` that can become this `$a0`,
and every `jal rs_free` that can receive that pointer. Include
any overlay duplicate of `unregisterServiceWorker` /
`0x800070BC` if it is a second generated body of the same PCs.
Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are
covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_2.c
    grep -n -- 'unregisterServiceWorker\|0x800070BC\|0x80007128' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x28D0\|0x801128D0' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
