# NEXT work unit — load_full_header_image rs_free of $s1

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of
`load_full_header_image` `jal rs_free` at
`0x800544D8` (`$a0` = `$s1` = matching
`get_asset_size_extra` `rs_malloc` at `0x80054428`,
flags-0; DMA dest then `sh` a halfword at `0x80137C70`
in the delay slot of the free). Enumerate every original
load/store of `$s1` (including the DMA dest, every later
store that can become this `$a0`, and whether any caller
holds the buffer) and every `jal rs_free` that can receive
that pointer. Do not repeat the closed
attachedMeshOverlayNpcHandler `0x1C`/`0x20` (Gap, s3636;
sibling `freeListEntryPointers` unreferenced),
loadAssetIntoNewSlot `$s6`,
freeAnimationPhasePool slot `+0x0` / `0x80137C84`,
loadAssetAndIterateSubchunks `$s6`, freeAllHobFiles slot
`+0x8`, releaseMeshAsset `$s5`, load_hmt_and_hob
`$s3`/`0x6C`/`0x74`, freeSubtitleOverlay `*0x80139010`,
freeTxtFile globals, loadSpriteSheetTextureFrames
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
writer and assessing legitimacy. Do not land a skip-path
NULL store for the s3636 overlay Gap unless this census
identifies that same writer as this `$s1`.

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
of `$s1` in `load_full_header_image` and every caller-side
store that can become this `$a0`, and every `jal rs_free`
that can receive that pointer.
Select Gap only with a concrete non-allocator or
already-freed edge; select Complete only when all remaining
edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_11.c
    grep -n -- 'load_full_header_image' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x800544D8\|0x80054428\|0x80054444' ../N64Recomp/RecompiledFuncs/funcs_11.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
