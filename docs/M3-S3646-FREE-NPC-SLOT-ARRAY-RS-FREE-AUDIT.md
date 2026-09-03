# M3 s3646 — freeNpcSlotArray rs_free of *0x80130BB0

## Work unit

Static census of `freeNpcSlotArray` `jal rs_free`
at `0x8003FC0C` (`$a0` = `*0x80130BB0`). Enumerated
every original load/store of that word (including the
matching malloc store in `initNpcSlotList` at
`0x8003E584`, every later store that can become this
`$a0`, and whether any caller holds the buffer) and
every `jal rs_free` that can receive that pointer.
`0x80130BB0` is the 8-byte-stride slot-chain table
consumed by `findActiveNpcInSlotChain` /
`destroyNpcSlotByIndex` / spawn walks; those loads
were classified as table-base consumers or as a
second free. No build or runtime run was performed.

The discriminator was the single complete original
census of that `jal rs_free` site plus every original
`lw`/`sw`/`addu` of `0x80130BB0` and every
caller-side store that can become this `$a0`, and
every `jal rs_free` that can receive that pointer.
No overlay duplicate of `freeNpcSlotArray` /
`0x8003FBF8` exists.

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

Closed classes were not repeated: destroyNpcContextArrays
`*0x80130BC0`/`*0x80130BC4`/`*0x80130BBC`/`*0x80130BB8`,
freeNpcBurstSpawnerTables `*0x80130BD0`/`*0x80130C08`/
`*0x80130C04`, computeGridTileEdgeAdjacencyMasks `$s1`,
teardownAnimatedMapGridLayer remaining
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
same writer as this word.

Sibling `reinsertNpcIntoSortedFreeList` `0x4($npc)`
at `0x8003EC34` is a different destructor of a
different word (`slotDispatcherInner`
`rs_malloc(0x204C, 0)` interior). It is not this
class.

## Census size

Original `jal 0x80001C98` in `funcs_9.c`: 14 sites.
One is this class (`0x8003FC0C`). Four are
`destroyNpcContextArrays` (closed s3645). Three
are `freeNpcBurstSpawnerTables` (closed s3644).
One is `computeGridTileEdgeAdjacencyMasks` (closed
s3643). Five are `teardownAnimatedMapGridLayer`
(closed s3642). None of those other thirteen loads
this word. `funcs_9.c` `jal rs_free` is exhausted.

`freeNpcSlotArray` is `0x8003FBF8`..`0x8003FC24`,
frame `-0x18`. One generated `jal 0x8003FBF8`
(`endMissionCleanup` `0x800FBAA4`). Zero
`LOOKUP_FUNC(0x8003FBF8)`. Single `jr $ra` at
`0x8003FC20`.

The body is: `lw $a0, 0xBB0($s0)` (`$s0` =
`lui 0x8013`), `jal rs_free`, then
`sw $zero, 0xBB0($s0)`. No NULL skip.

`initNpcSlotList` is `0x8003E560`..`0x8003E5F4`,
frame `-0x18`. Three generated `jal 0x8003E560`.
Zero `LOOKUP_FUNC(0x8003E560)`. Single `jr $ra`
at `0x8003E5F0`. The malloc store executes on
every entry.

No absolute `0x80130BB0` encodings exist outside
`lui 0x8013` plus `0xBB0`. No `-0xF450` alias
from `0x80140000`. No `addiu ..., 0xBB0`. Three
`lui 0xBB00` sites (`emitMaterialTexturedDL` /
`emitMaterialTexturedDLAlt` /
`emitMaterialRenderStateDL`) are GBI immediates,
not this word.

`funcs_8.c` has one `jal rs_free`
(`0x8003EC34`): `$a0` is `0x4($npc)` on the
bit-`0x4` skip of `reinsertNpcIntoSortedFreeList`,
not this word.

## Object identity

### `0x80130BB0` — 0x800-entry slot table, stride 8

`rs_malloc(0x4000, 0)` at `0x8003E574`. Delay-slot
`sw $v0, 0xBB0($s0)` at `0x8003E584` (`$s0` =
`lui 0x8013`). `0x4000 / 8 = 0x800`. Only
original heap-pointer store of the word.

The fill then walks `$a2 = $v0` for 0x800
iterations: `sw $zero, 0x0($slot)`,
`sh i-1, 0x6($slot)`, `sh i+1, 0x4($slot)`.
Those are interiors of the buffer, not a second
store of `0x80130BB0`. After the walk, init
reloads the word and writes sentinel halfwords
on slot 0 (`+0x4/+0x6/+0xC/+0xE/+0x16`) and
the last slot (`+0x3FFC` = entry `0x7FF` `+0x4`).

`0x80130BB4` is a free-list head halfword. Init
stores `2`. `allocateNpcSlot` /
`popNpcSlotFromTail` /
`unregisterAndFreeNpcSlot` /
`destroyNpcSlotByIndex` /
`destroyNpcSlotChain` load and store that
halfword as an index. It is not a pointer and
is not this class.

The only other original store of `0x80130BB0`
is the destructor `sw $zero` at `0x8003FC18`.

## Consumers

Fifty-seven original loads use the word as a
table base (`base + index*8`), then read
`+0x0` (NPC pointer or 0), `+0x4` (next index),
`+0x6` (prev index), or slot-0 chain
halfwords `+0xC/+0xE/+0x16`. None `jal rs_free`
of the loaded word.

| Function | Role |
|---|---|
| `allocateNpcSlot` | pop free-list head; write `+0x4/+0x6` and `+0x0` |
| `popNpcSlotFromTail` | same free-list pop; attach NPC at `+0x0` |
| `unregisterAndFreeNpcSlot` | relink `+0x4/+0x6` and push the index onto `0xBB4`. Loads into `$a0` are `addu` table-base arithmetic, then `jr $ra`. No `jal rs_free` |
| `slotDispatcherIter` | walk `+0x0` NPC and `+0x4` next |
| `destroyNpcSlotByIndex` | load `+0x0`, then `jal` the NPC destructor and `unregisterAndFreeNpcSlot` |
| `revalidateNpcSlotIterator` | table-base walk |
| `relinkNpcSlotToNewParentGroup` | table-base walk |
| `destroyNpcSlotChain` | walk `+0x4`; `jal unregisterAndFreeNpcSlot` of each live `+0x0` |
| `spawnChildNpcWithTransform` | table-base + parent-index `+0x4` walk. The `$a0` load at `0x8003F4A0` is that table base, not a free |
| `spawnInheritedNpcVariantA/B/C` | table-base spawn walk |
| `findActiveNpcInSlotChain` | table-base search |
| `findFirstActiveNpcChildInChain` | table-base search |
| `spawnNpcWithSubtype` / `spawnNpcOfType` | table-base; walk slot-0 `+0xE` chain |
| `getNpcContextByIndex` / `getNpcContextField8` | table-base lookup |
| `findFreeNpcSlotByKey` | table-base search |
| `getNextSlotNpcTypeId` / `getNpcNextSlotIndex` | table-base lookup |
| `destroyTransientNpcSlots` | table-base; walk `+0xE` and `jal destroyNpcSlotByIndex` |

`unregisterAndFreeNpcSlot` frees a *slot index*
back onto the halfword free list. It does not
heap-free the table. Interior `+0x0` stores are
NPC pointers or 0, not a second heap pointer
into `0x80130BB0` itself.

No generated caller holds a copy of the table
pointer across the destructor. Spawn and
dispatch consumers load the global each time.

## Pairing

`initNpcSlotList` has three generated callers:

| Caller | PC |
|---|---|
| `initMission` | `0x800FA28C` |
| `initSceneForMission` | `0x800A9C94` |
| `initInteractiveSceneContext` | `0x800C4154` |

It always overwrites `0x80130BB0` with a fresh
allocator return and does not free the previous
word. Menu `initInteractiveSceneContext` without
this destructor leaks the first malloc; that is
not a second pointer source.

`endMissionCleanup` has two generated callers,
both in `mainGameLoop`: `0x8003E2C4` and
`0x8003E388` (`LOOKUP_FUNC(0x800FB9E4)`). Those
arms are mutually exclusive (s3624). Sequential
double-free of a live table is blocked by that
pairing plus the post-free NULL. A second call
would `rs_free(NULL)`.

The s3636 overlay `0x1C`/`0x20` writer is a
different `rs_malloc(0x80, 0)` and is not this
word.

## Verdict

H-NextClassComplete. Matching flags-0
`rs_malloc(0x4000, 0)` of `0x80130BB0`
(0x800 × 8-byte slot table). One destructor
via two mutually exclusive `mainGameLoop`
arms; post-free NULL; no NULL skip. Consumers
load the word as a table base and do not
`jal rs_free`. No second live `jal rs_free`
of that pointer. H-NextClassGap is refuted at
static scope. Runtime allocator legitimacy
(including `rs_free` of a NULL malloc return,
and leak of a second init without this
destructor) remains unproven. No guard was
added.
