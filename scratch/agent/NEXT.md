# NEXT work unit — freeTxtFile rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of
`freeTxtFile` `jal rs_free` at `0x800558F8` and
`0x80055910` (`$a0` = `*0x8009ECA0` then `*0x8009ECA8`,
`lui $s3/$s2, 0x800A` + `-0x1360`/`-0x1358`, each
NULL-skipped). Enumerate every original load/store of
those two words (including `loadVoiceTxtFile` and any
other writer) and every `jal rs_free` that can receive
them. Classify each pointer's writer and whether a free
can run on a non-allocator or already-freed value. The
following `teardownAssetDma` of `*0x8009ECA4` when that
word is not `-1` is in scope only as a sibling lifetime
edge, not as a third `rs_free`. Do not repeat the closed
loadSpriteSheetTextureFrames inlined-malloc,
loadAndRelocateAsset load_asset, loadExplosionTextures
load_asset, freeEffectAssetBuffers globals,
loadSkyHorizonHob stack scratch,
cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
spawnCutsceneObjectsFromList 0x6C, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor +0x4C, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch rs_free, text-texture rs_free, format-message
rs_free, speech-file rs_free, speech/cache rs_free, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT publication,
mix-table, pan-input, or hangar-Y audits. Do not change
runtime code unless a concrete invalid writer/value is
identified; any mitigation needs an ORIGIN line naming the
writer and assessing legitimacy.

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
two `jal rs_free` sites plus every original `lw`/`sw` of
`0x8009ECA0` and `0x8009ECA8` and every `jal rs_free` that
can receive either word. Select Gap only with a concrete
non-allocator or already-freed edge; select Complete only
when all remaining edges are covered; otherwise select
Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_12.c
    grep -n -- 'freeTxtFile\|loadVoiceTxtFile' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x800558F8\|0x80055910\|0x8009ECA0\|0x8009ECA8' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
