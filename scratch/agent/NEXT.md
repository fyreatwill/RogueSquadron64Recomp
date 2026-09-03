# NEXT work unit — teardownAnimatedMapGridLayer remaining rs_free

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of
`teardownAnimatedMapGridLayer` remaining `jal rs_free`
at `0x80045730` (`$a0` = `*0x80136DC8`), plus the
sibling frees of `*0x80136DCC` at `0x8004573C`,
`*0x80136FC4` at `0x80045748`, `*0x80136FCC` at
`0x80045780`, and `*0x80136E1C` at `0x80045790`.
Enumerate every original load/store of those five
words (including the matching `rs_malloc` of the
`loadLevelAssets` `n*24` sibling at `0x80136E1C`,
every later store that can become these `$a0`s, and
whether any caller holds the buffers) and every
`jal rs_free` that can receive those pointers. Do
not repeat the closed teardownGridLayerWorker
`*0x80137614`, freeGridCellBuffers
`*0x80137A5C`/`*0x80137A54`/`*0x80137A4C`/
`*0x80137A68`, loadLevelTextureCache `$s0` 0x136C
scratch, freeLevelDatBuffers `*0x801375D0`/
`*0x801375D8`/`*0x801375F4`, load_full_header_image
`$s1`, attachedMeshOverlayNpcHandler `0x1C`/`0x20`
(Gap, s3636; sibling `freeListEntryPointers`
unreferenced), loadAssetIntoNewSlot `$s6`,
freeAnimationPhasePool slot `+0x0` / `0x80137C84`,
loadAssetAndIterateSubchunks `$s6`, freeAllHobFiles
slot `+0x8`, releaseMeshAsset `$s5`, load_hmt_and_hob
`$s3`/`0x6C`/`0x74`, freeSubtitleOverlay
`*0x80139010`, freeTxtFile globals,
loadSpriteSheetTextureFrames inlined-malloc,
loadAndRelocateAsset load_asset,
loadExplosionTextures load_asset,
freeEffectAssetBuffers globals, loadSkyHorizonHob
stack scratch, cinematicSplineWalkerNpcHandler
nested 0xF00/0x2B44, spawnCutsceneObjectsFromList
0x6C, NPC allocateAndInit destructor, player-craft
`+0xBC`, playerAtStUpdate 0xA4/0xBC, actor +0x4C,
tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch rs_free, text-texture rs_free,
format-message rs_free, speech-file rs_free,
speech/cache rs_free, destructor skipped-NULL,
destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, or hangar-Y
audits. Do not change runtime code unless a concrete
invalid writer/value is identified; any mitigation
needs an ORIGIN line naming the writer and assessing
legitimacy. Do not land a skip-path NULL store for
the s3636 overlay Gap unless this census identifies
that same writer as one of these five words.

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
`jal rs_free` sites plus every original `lw`/`sw`/`addu`
of `0x80136DC8` / `0x80136DCC` / `0x80136FC4` /
`0x80136FCC` / `0x80136E1C` and every caller-side store
that can become these `$a0`s, and every `jal rs_free`
that can receive those pointers.
Select Gap only with a concrete non-allocator or
already-freed edge; select Complete only when all remaining
edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_9.c
    grep -n -- 'teardownAnimatedMapGridLayer\|loadLevelAssets' ../N64Recomp/RecompiledFuncs/funcs_*.c
    grep -n -- '0x80045730\|0x80136DC8\|0x80136DCC\|0x80136FC4\|0x80136FCC\|0x80136E1C\|0x6DC8\|0x6DCC\|0x6FC4\|0x6FCC\|0x6E1C' ../N64Recomp/RecompiledFuncs/funcs_9.c

No build or runtime run is expected for this static audit. If
the census is complete, write a new `docs/M3-S<session>-...md`
evidence note and update CURRENT-TRUTH, the ledger, status,
outcome, and commit.
