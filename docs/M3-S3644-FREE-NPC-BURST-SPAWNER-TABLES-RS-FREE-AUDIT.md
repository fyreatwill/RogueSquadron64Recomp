# M3 s3644 — freeNpcBurstSpawnerTables rs_free of *0x80130BD0 / *0x80130C08 / *0x80130C04

## Work unit

Static census of `freeNpcBurstSpawnerTables` `jal rs_free`
at `0x80041B58` (`$a0` = `*0x80130BD0`), `0x80041B68`
(`$a0` = `*0x80130C08`), and `0x80041B78` (`$a0` =
`*0x80130C04`). Enumerated every original load/store of
those three words (including the matching malloc stores
at `0x80040334` / `0x800403A8` / `0x800403B8`, every
later store that can become these `$a0`s, and whether
any caller holds the buffers) and every `jal rs_free`
that can receive those pointers. No build or runtime
run was performed.

The discriminator was the single complete original
census of those `jal rs_free` sites plus every original
`lw`/`sw`/`addu` of `0x80130BD0` / `0x80130C08` /
`0x80130C04` and every caller-side store that can
become these `$a0`s, and every `jal rs_free` that can
receive those pointers. No overlay duplicate of
`freeNpcBurstSpawnerTables` / `0x80041B48` exists.

- H-NextClassGap: a remaining free can pass a pointer
  that is not the matching allocator store, or can
  free it after a sibling already released it without
  a NULL.
- H-NextClassComplete: every remaining free is a
  destructor of a matching init store, and only
  runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or
  unshared writers prevent a complete classification
  of a pointer source.

Closed classes were not repeated: computeGridTileEdgeAdjacencyMasks
`$s1`, teardownAnimatedMapGridLayer remaining
`*0x80136DC8`/`*0x80136DCC`/`*0x80136FC4`/
`*0x80136FCC`/`*0x80136E1C`, teardownGridLayerWorker
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
publication, mix-table, pan-input, or hangar-Y.
Do not land a skip-path NULL store for the s3636
overlay Gap unless this census identifies that
same writer as one of these three words.

## Census size

Original `jal 0x80001C98` in `funcs_9.c`: 14 sites.
Three are this class (`0x80041B58` / `0x80041B68` /
`0x80041B78`). One is `computeGridTileEdgeAdjacencyMasks`
(closed s3643). Five are `teardownAnimatedMapGridLayer`
(closed s3642). Four are `destroyNpcContextArrays`.
One is `freeNpcSlotArray`. None of those eleven loads
these three words.

`freeNpcBurstSpawnerTables` is `0x80041B48`..`0x80041B88`,
frame `-0x18`. One generated `jal 0x80041B48`
(`endMissionCleanup` `0x800FBA7C`). Zero
`LOOKUP_FUNC(0x80041B48)`. Single `jr $ra` at
`0x80041B84`. The body is straight-line: no original
branch skips any of the three frees. No NULL skip
and no post-free NULL.

`allocAndInitParticlePool` is `0x80040310`..`0x800403E8`,
frame `-0x20`. Three generated `jal 0x80040310`. Zero
`LOOKUP_FUNC(0x80040310)`. Single `jr $ra` at
`0x800403E4`. All three pointer stores execute on
every entry.

No absolute `0x80130BD0` / `0x80130C08` / `0x80130C04`
encodings exist outside `lui 0x8013` plus `0xBD0` /
`0xC08` / `0xC04`. No `-0xF430` / `-0xF3F8` /
`-0xF3FC` aliases from `0x80140000`. Coincidental
`0xC08`/`0xC04` loads with a non-`0x8013` base, and
the two `swc2 0xC08` sites, are different objects.
Interior `0xC04(*0x80130C04)` after `addiu $v0, 0xC0`
is a field of the buffer, not the global.

## Object identity

### `0x80130BD0` — 128-slot particle pool, stride 0x6C

`rs_malloc(0x3600, 0)` at `0x8004031C` (`0x80 * 0x6C`).
`sw $v0, 0xBD0($v1)` at `0x80040334` (`$v1` = `lui 0x8013`).
Only original store of the word.

A 0x80-iter walk then writes prev/next halfwords at
`+0x0`/`+0x2` with stride 0x6C (`-1` at the ends).
`0x80130BD4` is a free-list head halfword (`sh $zero`
at `0x8004038C`); it is not a pointer and is not
freed.

Consumers (`spawnNpcFormationWithRandomOrientation`,
`computeNpcGroupCentroidAndCull`) load the word as
the pool base and add `index * 0x6C`. Interior
halfword/`swc1` stores die with the buffer. None
`jal rs_free`.

### `0x80130C08` — `loadAssetAndIterateSubchunks` index table

`jal loadAssetAndIterateSubchunks` at `0x80040390`
with `$a2 = 0`. Delay-slot `sw $v0, 0xC08($v1)` at
`0x800403A8` stores that return (`$s4`), not the
callee's DMA `$s6`. `$a2 == 0` mallocs
`(count+1)<<1` flags-0 and writes a `0xFFFF`
terminator (closed s3633). Zero chunk count still
mallocs a 2-byte table. Only original store of the
word.

Consumers load the word as a name/id table base
(spawn/debris/effect/hangar/wingman/walker paths).
`spawnRandomBurstNpc` copies it into stack
`0x64($sp+0x10)` / `0x74($sp)` as a
`spawnNpcOfType` extra-arg slot. None `jal rs_free`.

### `0x80130C04` — `load_asset` buffer

`jal load_asset` at `0x800403A4`. After return,
`sw $v0, 0xC04($a1)` at `0x800403B8` (`$a1` =
`lui 0x8013`). `load_asset` returns its
`rs_malloc(get_asset_size_extra(...), 0)`. Only
original store of the word.

A 0x80-iter walk then copies `lbu 0x200($v0)` to
`sb 0x3($v0)` inside the buffer. Consumers load
the word as a table base; several copy it to a
callee-stack extra-arg slot (`0x78($sp)` /
`0xA8($sp)`). None `jal rs_free`.

No other generated `jal 0x80001C98` loads any of
the three words into `$a0`.

## Pairing

`allocAndInitParticlePool` has three generated
callers:

| Caller | PC |
|---|---|
| `initMission` | `0x800FA2E4` |
| `setupCutsceneLevel` | `0x800A6F90` |
| `initInteractiveSceneContext` | `0x800C416C` |

It always overwrites all three globals with fresh
allocator returns and does not free the previous
values. `initInteractiveSceneContext` is reached
only via `menuSubtype02Handler` `jal 0x800C3FE0`.
Menu init without this destructor leaks the first
malloc; that is not a second pointer source.

`endMissionCleanup` has two generated callers, both
in `mainGameLoop`: `0x8003E2C4` and `0x8003E388`
(`LOOKUP_FUNC(0x800FB9E4)`). Those arms are
mutually exclusive (s3624). Sequential double-free
of the three words is blocked by that pairing.
The destructor does not NULL the words after free.

The s3636 overlay `0x1C`/`0x20` writer is a
different `rs_malloc(0x80, 0)` and is not one of
these three words.

## Verdict

H-NextClassComplete. Three matching allocator
stores, one destructor, no caller-held copy that
`jal rs_free`, no second live `jal rs_free` of
those pointers. H-NextClassGap is refuted at
static scope. Runtime allocator legitimacy
(including `rs_free` of a NULL malloc return)
remains unproven. No guard was added.
