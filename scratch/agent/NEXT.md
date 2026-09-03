# NEXT work unit — freeManifestSegmentAssets 0x40($s0) rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Session 3656 closed `findManifestEntryByName`
`$s2` at `0x8000490C` as Complete. That
8-byte flags-9 malloc is register-local
header scratch, not the DMA-slot payload.
The live M3 unit is the next remaining
original `jal 0x80001C98` in `funcs_1.c`,
which shares a word with its sibling.

Next work unit: perform one complete static census of
`freeManifestSegmentAssets` `jal rs_free` at
`0x80004A0C` (`$a0` = `0x40($s0)` from
`lw $a0, 0x40($s0)` at `0x80004A08`).
Include the sibling `jal rs_free` at
`0x80004A80` (`lw $a0, 0x40($s0)` at
`0x80004A7C`) in the same census: both
load the 0x50-stride DMA-slot word at
`0x80110A80 + idx*0x50 + 0x40`.
Enumerate every original load/store of
that `0x40($s0)` (including the matching
allocator `findManifestEntryByName`
`rs_malloc` store at `0x80004920`, every
later store, whether the caller holds the
buffer, the post-free `sb $zero, 0x4E($s0)`
busy-clear, and any sibling `jal rs_free`
of the same pointer or of adjacent slot
words) and every `jal rs_free` that can
receive that pointer. Classify other
loads as consumers or as a second free.
Do not repeat the closed classes
archived in PROJECT-OVERVIEW §56
(s3586–s3656 Complete/Unevaluable
families through `findManifestEntryByName`
`$s2`, plus the s3636 Gap at
`attachedMeshOverlayNpcHandler`
`0x1C`/`0x20`). Do not change runtime code
unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN
line naming the writer and assessing
legitimacy. Do not land a skip-path NULL
store for the s3636 overlay Gap unless this
census identifies that same writer as this
`0x40($s0)`.

If this census closes those sites, continue
with the next remaining original
`jal 0x80001C98` in `funcs_1.c`
(`0x80005000`).

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
of `freeManifestSegmentAssets` `0x40($s0)` that can become
this `$a0`, every original `lw`/`sw` of the same slot field,
and every `jal rs_free` that can receive that pointer. Include
any overlay duplicate of `freeManifestSegmentAssets` /
`0x80004994` if it is a second generated body of the same PCs.
Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are
covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_1.c
    grep -n -- 'freeManifestSegmentAssets\|0x80004994\|0x80004A0C\|0x80004A80' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x40(\$s0)\|0x40(\$s3)\|sw          \$v0, 0x40' ../N64Recomp/RecompiledFuncs/funcs_1.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
