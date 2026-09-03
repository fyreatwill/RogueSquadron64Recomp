# M3 s3636 — attachedMeshOverlayNpcHandler rs_free of 0x1C($s0)

## Work unit

Static census of `attachedMeshOverlayNpcHandler` `jal rs_free`
at `0x80054344` (`$a0` = `0x1C($s0)`, two-iter `+0x4` walk so
the second pass is `0x20($s0)`; `$s0` starts as `$s2` =
`0x4($s1)` on opcode 2). Enumerated every original load/store
of those two words (including the matching `rs_malloc`, every
later store that can become this `$a0`, and the sibling
`freeListEntryPointers` `0x80054620` walk of the same pair)
and every `jal rs_free` that can receive those pointers. No
build or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of `0x1C($s0)` / `0x20($s0)` on the `0x4($s1)` object and
every caller-side store that can become this `$a0`, and
every `jal rs_free` that can receive those pointers:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadAssetIntoNewSlot `$s6`,
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
mix-table, pan-input, or hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_11.c`: 7 sites. Two are
this class (`attachedMeshOverlayNpcHandler` `0x80054344` and
sibling `freeListEntryPointers` `0x80054620`). The other five
are `load_full_header_image` `0x800544D8` (`$s1`),
`loadAssetIntoNewSlot` `0x800549E4` (closed s3635),
`freeAnimationPhasePool` `0x80054AC8`/`0x80054AEC`
(closed s3634), and `loadAssetAndIterateSubchunks`
`0x8005519C` (closed s3633). None of those five loads this
object's `0x1C`/`0x20`.

`attachedMeshOverlayNpcHandler` is `0x8005427C`..`0x800543F4`,
frame `-0x30`. Zero generated `jal 0x8005427C`. Nine
`lui 0x8005` / `addiu 0x427C` constructions pass it to
`spawnNpcOfType` (`$a2=1`, `$a3=0x64`):
`playerSnowSpeederUpdate`, `playerXwingUpdate`,
`playerAwingUpdate`, `playerYwingUpdate`,
`playerVwingUpdate`, `playerFalconUpdate`,
`playerTieInterceptorUpdate`, `playerT16Update`,
`playerNabooStarfighterUpdate`. Zero
`LOOKUP_FUNC(0x8005427C)`. Dispatch is `slotDispatcherIter`
`jalr` of wrapper `+0x0`. Single `jr $ra` at `0x800543EC`.

`freeListEntryPointers` is `0x80054600`..`0x80054648`. Zero
generated `jal 0x80054600`, zero `LOOKUP_FUNC`, zero
`lui 0x8005` / `addiu 0x4600`. ROM word `0x80054600` is
absent. The sibling destructor is unreferenced at generated
call scope.

Original `0x1C`/`0x20` accesses on this object:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| pool carve | `0x8003EB48` | `sw $v0, 0x4($s1)` | wrapper `+0x4` | `slotDispatcherInner` body; 128-byte slot (`+0x14` bit 0); no memset of `+0x1C`/`+0x20` |
| type skip | `0x80053D34` | `bltz` after `sh $v1, 0x2($s3)` | overlay | unmatched parent name writes type `-1` and skips the malloc loop; `0x1C`/`0x20` unwritten |
| malloc | `0x80053DA0`/`0x80053DBC` | `jal rs_malloc(0x80, 0)`; delay-slot `sw $v0, 0x1C($s0)` | `0x1C` then `0x20` | only original heap-pointer writer; `$s0` starts as `$s3`, `+0x4` per iter, two iters |
| memcpy dest | `0x80053DEC` | `lw $a0, 0x1C($s0)` | same | `zmemcpy` 0x80 from node `+0x24`; not a store |
| tick consume | `0x80054160`/`0x800541E8` | `lw $s4, 0x1C($s0)` / `0x20($s0)` | same | `updateAnimatedTextureStreaming` (opcode 4); s127 KSEG0 skip already in generated code |
| opcode 2 free | `0x8005433C`/`0x80054344` | `lw $a0, 0x1C($s0)`; `$s0+=4`; `jal rs_free` | `$s2=0x4($s1)` | destructor; two iters; no NULL skip; no post-free NULL |
| sibling free | `0x80054618`/`0x80054620` | same walk on `$a0` | caller object | unreferenced |

Other original `0x1C($s0)` / `0x20($s0)` stores in `funcs_11.c`
(`initPlayerVehicleStateTables`, `resetEffectObjectVecQuads`,
`initEffectObjectDefaults`, `initTransformNodeFromVectors`,
`spawnRandomizedEffectBurst`, `spawnScatteredDebrisParticles`,
`initEffectObjectFromLevelData`) are different objects.
`freeMenuScreenState` `0x800C549C` walks `0x18`/`0x1C`/`0x20`
of a menu screen, not this overlay.

## Object identity

`$s1` is incoming `$a0` (NPC wrapper). `$s2 = 0x4($s1)` is the
actor body. `spawnNpcOfType` zeros wrapper `+0x4`, stores the
handler at `+0x0` and `$a2` at `+0x14`, then
`slotDispatcherInner` carves a pool slot and stores it at
`+0x4`. Generated overlay spawns pass `$a2=1` (bit 0, not bit
`0x4`), so the body is the 128-byte pool slot, not the
`allocAndSetupModelInstance` heap `0x34`.

Opcode 1 writes `lhu 0x0($a2)` to `0x0($s2)`, looks up the
parent NPC, and on a non-NULL parent mesh at `+0xC` calls
`dispatchOverlaySetupByParentAssetName($s0=mesh, $s1=$s2)`.
A NULL parent mesh calls `destroyNpcSlotByIndex` (deferred
opcode 2 because wrapper `+0x1A != 0` during the `jalr`) and
skips the malloc.

`dispatchOverlaySetupByParentAssetName` strcmp's `0x0(mesh)`
against `awing`, `vwing`, `xwing`, `ywing`, `snowspeeder`,
`falcon`, `tie_inter`, `koelsch`, `t16`. A match stores type
`0..8` at `+0x2` and runs the two-iter `rs_malloc(0x80, 0)`
into `0x1C` then `0x20`. No match stores type `-1` and
`bltz`-skips the loop. The skip does not `sw $zero` those
words. ROM has no `naboo`/`Naboo` string; the ninth spawn
site is `playerNabooStarfighterUpdate`.

Opcode 2 always walks `0x1C`/`0x20` and `rs_free`s. `rs_free`
itself `beq $s0, $zero` at `0x80001CA4`; a NULL `$a0` is a
skip. Unwritten pool words are not proven NULL:
`slotDispatcherInner` does not memset the carved slot, and
`rs_malloc` of the `0x204C` pool uses flags-0.

`destroyNpcSlotByIndex` sends opcode 2 once (`jalr` `$a1=2`)
then `reinsertNpcIntoSortedFreeList`, which returns the slot
to the `0x80130BC0` pool (flag `0x4` unset) without NULLing
`0x1C`/`0x20`. Sequential opcode-2 is one send per destroy.

### `allocAndSetupModelInstance` — disjoint 0x34 heap object

Four generated callers (`spawnCutsceneObjectsFromList` stores
`$v0` at cutscene actor `+0x60`; `mallocCraftSelectionData` at
`+0x20C`; `setupCraftPreviewModel` at `+0x14`;
`loadModelViewerModels` at `+0x8C`) `rs_malloc(0x34)` and call
the same setup. That is a different object. `setupCraftPreviewModel`
`rs_free`s the `0x34` when `lh +0x2 < 0` (malloc loop skipped;
inner `0x1C`/`0x20` were never written). No generated caller
of `freeListEntryPointers` frees those inner words. A leak of
the `0x80` buffers on the keep path is not a second pointer
source for this `$a0`.

Opcode 4 (`updateAnimatedTextureStreaming`) loads `0x1C`/`0x20`
as texture-list bases. The s127 KSEG0 skip in that consumer is
independent evidence that those words can be non-heap.

## Pairing

On a matched parent name, the two-iter malloc is the matching
init and opcode 2 is the matching destructor. On an unmatched
name, or on a NULL parent mesh, opcode 2 still runs and the
words are not this occupancy's allocator store. That is a
concrete non-allocator edge. The unreferenced sibling
`freeListEntryPointers` cannot double-free the pool body at
generated-call scope. Runtime whether Naboo's mesh name misses
the nine-string table, and whether reused pool slots hold
non-NULL garbage, remains unproven.

## Classification

The only live `jal rs_free` site that can receive this
pointer is `0x80054344`. The only original heap-pointer
writer of `0x1C`/`0x20` on this object is the flags-0 malloc
at `0x80053DBC`. That writer does not run on the type-`-1`
or NULL-parent paths, and neither path stores NULL first.
This selects `H-NextClassGap`. `H-NextClassComplete` is
refuted: opcode 2 is not always a destructor of a matching
init store. `H-NextClassUnevaluable` is not selected: one
overlay-buffer identity and one allocator store of that
pair, plus a classified skip with no store.

No guard was added. A skip-path `sw $zero` of `0x1C`/`0x20`
in `dispatchOverlaySetupByParentAssetName` would make the
free a NULL skip; that is a game-side init store, not a
host pointer check, and was not landed in this no-build
census. Runtime occupancy of the skip path remains unproven.

## Next remaining `jal rs_free`

Remaining in `funcs_11.c`: `load_full_header_image`
`0x800544D8` (`$a0` = `$s1` = matching
`get_asset_size_extra` `rs_malloc`). `funcs_11.c`
`jal rs_free` of overlay `0x1C`/`0x20` is exhausted.
`freeListEntryPointers` is the unreferenced sibling of
this class, not a separate remaining site.
