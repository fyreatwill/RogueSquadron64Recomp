# NEXT work unit — findManifestEntryByName $s2 rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3655 closed `processAssetLoadStep`
`0x48($s0)` / `mainEventQueueWorker`
`0x8000450C` as Complete. Those two
original `jal 0x80001C98` sites share the
event-queue slot field. The live M3 unit
is the first remaining original
`jal 0x80001C98` in `funcs_1.c`.

Next work unit: perform one complete static census of
`findManifestEntryByName` `jal rs_free` at
`0x8000490C` (`$a0` = `$s2` from
`addu $a0, $s2` at `0x80004900`).
Enumerate every original load/store of
that `$s2` (including the matching
allocator if any, every later store,
whether the caller holds the buffer, the
delay-slot `lw $s2, 0x0($a0)` at
`0x80004908` / `and $s0, $s0, $v0` at
`0x80004910`, and any sibling
`jal rs_free` of the same pointer or of
adjacent words) and every `jal rs_free`
that can receive that pointer. Classify
other loads as consumers or as a second
free. Do not repeat the closed classes
archived in PROJECT-OVERVIEW §56
(s3586–s3655 Complete/Unevaluable
families through `processAssetLoadStep`
`0x48($s0)`, plus the s3636 Gap at
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
with the next remaining original
`jal 0x80001C98` in `funcs_1.c`
(`0x80004A0C`).

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
`findManifestEntryByName` `$s2` that can become this `$a0`,
and every `jal rs_free` that can receive that pointer. Include
any overlay duplicate of `findManifestEntryByName` /
`0x800047F4` if it is a second generated body of the same PCs.
Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are
covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_1.c
    grep -n -- 'findManifestEntryByName\|0x800047F4\|0x8000490C' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- 'addu        \$a0, \$s2\|lw          \$s2' ../N64Recomp/RecompiledFuncs/funcs_1.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
