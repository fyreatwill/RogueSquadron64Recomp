# NEXT work unit — remaining actor +0x4C rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every generated
original `jal rs_free` of actor field `+0x4C` in `npcAtAtUpdate`
and `npcAtStUpdate`. Remaining funcs_37 actor frees after the
closed tickMultiPartVoiceLine class: `0x800CDE8C` of `0x4C($s1)`
and `0x800D0480` of `0x4C($s2)`. Classify each pointer's writer
and whether a free can run on a non-allocator or already-freed
value. Do not include `playerAtStUpdate`'s `0xA4`/`0xBC` frees.
Do not repeat the closed tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table, loadCharTextureSet
DMA-array, load_asset-then-free, texture-scratch rs_free,
text-texture rs_free, format-message rs_free, speech-file rs_free,
speech/cache rs_free, destructor skipped-NULL, destructor
unchecked-free, `-0x6904` alias, remaining-indexer, `-0x6908`
non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, or hangar-Y audits. Do not
change runtime code unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN line naming the writer
and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Discriminator: the single complete original census of those
`jal rs_free` sites plus every original `sw` of `+0x4C`. Select
Gap only with a concrete non-allocator or already-freed edge; select
Complete only when all remaining edges are covered; otherwise select
Unevaluable.

Exact checks before any build:

    grep -n -- 'npcAtAtUpdate\|npcAtStUpdate' ../N64Recomp/RecompiledFuncs/funcs_37.c | head
    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_37.c
    grep -n -- '0x800CDE8C\|0x800D0480\|0x800D0DC0' ../N64Recomp/RecompiledFuncs/funcs_37.c

No build or runtime run is expected for this static audit. If the census
is complete, write a new `docs/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
