# NEXT work unit — remaining NPC allocateAndInit destructor rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every
generated original `jal rs_free` in remaining
`allocateAndInitCraftNpcContext` callers outside the closed
AT-AT/AT-ST `+0x4C` and player-craft table `+0xBC` paths:
`splineWalkerCraftNpcHandler` `0x8006C4A8`,
`stubNpcHandler` `0x8006C650`,
`npcProbeDriod` `0x800CAF3C`,
`npcWingmanUpdate` `0x800D9854`,
`npcTieVariantUpdate` `0x800DB760`,
`npcGroundTransportUpdate` `0x800DEE4C`,
`npcTrainCarUpdate` `0x800E2E3C`,
`npcWaterCraftUpdate` `0x800E678C`,
`npcGroundTroopUpdate` `0x800E7FF8`,
`tickCraftWithPhasedDestruction` `0x800E9400`, and
`npcAtPtUpdate` `0x800EAAE4`. Classify each pointer's writer
and whether a free can run on a non-allocator or already-freed
value. Do not repeat the closed player-craft `+0xBC`,
playerAtStUpdate 0xA4/0xBC, actor +0x4C, tickMultiPartVoiceLine,
freeModelViewerMeshChain, shutdownModelViewer header-word,
lookup-table, loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch rs_free, text-texture rs_free, format-message
rs_free, speech-file rs_free, speech/cache rs_free, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT publication,
mix-table, pan-input, or hangar-Y audits. Do not change runtime
code unless a concrete invalid writer/value is identified; any
mitigation needs an ORIGIN line naming the writer and assessing
legitimacy.

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
`jal rs_free` sites plus every original store of the
`allocateAndInitCraftNpcContext` return in those eleven
functions. Select Gap only with a concrete non-allocator or
already-freed edge; select Complete only when all remaining
edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x8006BD18' ../N64Recomp/RecompiledFuncs/funcs_16.c ../N64Recomp/RecompiledFuncs/funcs_36.c ../N64Recomp/RecompiledFuncs/funcs_38.c ../N64Recomp/RecompiledFuncs/funcs_39.c
    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_16.c ../N64Recomp/RecompiledFuncs/funcs_36.c ../N64Recomp/RecompiledFuncs/funcs_38.c ../N64Recomp/RecompiledFuncs/funcs_39.c
    grep -n -- 'sw          $v0, 0x4C' ../N64Recomp/RecompiledFuncs/funcs_16.c ../N64Recomp/RecompiledFuncs/funcs_36.c ../N64Recomp/RecompiledFuncs/funcs_38.c ../N64Recomp/RecompiledFuncs/funcs_39.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
