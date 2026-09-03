# NEXT work unit — freeSubtitleOverlay rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of
`freeSubtitleOverlay` `jal rs_free` at `0x800562CC`
(`$a0` = `*0x80139010`, `lui $v0, 0x8014` + `-0x6FF0`,
no NULL skip, no post-free NULL). Enumerate every original
load/store of that word (including `initVoiceSubtitleSystem`
`rs_malloc(0x20, 0)` at `0x80055A78` and every overlay
consumer) and every `jal rs_free` that can receive it. The
preceding `resetPlayerSlotChannelTransform` of
`lhu *0x80139014` (`-0x6FEC`) is in scope only as a sibling
lifetime edge, not as a second `rs_free`. Do not repeat the
closed freeTxtFile globals, loadSpriteSheetTextureFrames
inlined-malloc, loadAndRelocateAsset load_asset,
loadExplosionTextures load_asset, freeEffectAssetBuffers
globals, loadSkyHorizonHob stack scratch,
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

Discriminator: the single complete original census of that
`jal rs_free` site plus every original `lw`/`sw` of
`0x80139010` (`-0x6FF0` from `0x80140000`) and every
`jal rs_free` that can receive that word. Select Gap only
with a concrete non-allocator or already-freed edge; select
Complete only when all remaining edges are covered; otherwise
select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_12.c
    grep -n -- 'freeSubtitleOverlay\|initVoiceSubtitleSystem' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x800562CC\|0x80139010\|-0x6FF0' ../N64Recomp/RecompiledFuncs/funcs_*.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
