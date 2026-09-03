# M3 s3642 — teardownAnimatedMapGridLayer remaining rs_free

## Work unit

Static census of `teardownAnimatedMapGridLayer` `jal rs_free`
at `0x80045730` (`$a0` = `*0x80136DC8`), plus the sibling
frees of `*0x80136DCC` at `0x8004573C`, `*0x80136FC4` at
`0x80045748`, `*0x80136FCC` at `0x80045780`, and
`*0x80136E1C` at `0x80045790`. Enumerated every original
load/store of those five words (including the matching
`rs_malloc` of the `loadLevelAssets` `n*24` sibling at
`0x80136E1C`, every later store that can become these
`$a0`s, and whether any caller holds the buffers) and
every `jal rs_free` that can receive those pointers. No
build or runtime run was performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original `lw`/`sw`/`addu`
of `0x80136DC8` / `0x80136DCC` / `0x80136FC4` /
`0x80136FCC` / `0x80136E1C` and every caller-side store
that can become these `$a0`s, and every `jal rs_free`
that can receive those pointers:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: teardownGridLayerWorker
`*0x80137614`, freeGridCellBuffers
`*0x80137A5C`/`*0x80137A54`/`*0x80137A4C`/`*0x80137A68`,
loadLevelTextureCache `$s0` 0x136C scratch,
freeLevelDatBuffers `*0x801375D0`/`*0x801375D8`/
`*0x801375F4`, load_full_header_image `$s1`,
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
mix-table, pan-input, or hangar-Y. Do not land a skip-path
NULL store for the s3636 overlay Gap unless this census
identifies that same writer as one of these five words.

## Census size

Original `jal 0x80001C98` in `funcs_9.c`: 14 sites. Five
are this class (`0x80045730` / `0x8004573C` /
`0x80045748` / `0x80045780` / `0x80045790`). One is
`computeGridTileEdgeAdjacencyMasks` `$s1` (local
`rs_malloc` of `lhu 0x18(*0x80136FC4)`, not these
words). Three are `freeNpcBurstSpawnerTables`. Four are
`destroyNpcContextArrays`. One is `freeNpcSlotArray`.
None of those nine loads these five words.

`teardownAnimatedMapGridLayer` is `0x80045708`..
`0x800457A8`, frame `-0x20`. Two generated `jal
0x80045708` (`endMissionCleanup` `0x800FBAB4`,
`cinematicShutdownAudioAndAssets` `0x800AF270`). Zero
`LOOKUP_FUNC(0x80045708)`; the only `0x53C8` immediate
is `lui 0x8010` / `addiu 0x53C8` in `funcs_46.c`
(`0x801053C8`, a `0x800C7830` argument, not this
function). `0x5708` immediates are `lwc1`/`lb` rodata,
not `0x80045708`. Single `jr $ra` at `0x800457A4`.

The body is two straight-line groups:

1. If `*0x80136FC4 == 0`, skip the first three frees.
   Otherwise `$s0 = 0x80136DC0`, free `0x8($s0)`
   (`0x80136DC8`), free `0xC($s0)` (`0x80136DCC`),
   free `*0x80136FC4`, then `sw $zero, 0x6FC4`. No
   NULL skip of the `+0x8`/`+0xC` words themselves.
2. If `*0x80130B70 == 0xA`, skip the rest. Otherwise
   `teardownGridLayerWorker` (closed s3641),
   `freeGridCellBuffers` (closed s3640), free
   `*0x80136FCC`, free `*0x80136E1C`. No NULL skip
   and no post-free NULL of those two words.

`loadLevelAssets` is `0x800453C8`..`0x800455C4`,
frame `-0x48`. Two generated `jal 0x800453C8`; zero
`LOOKUP_FUNC(0x800453C8)`. Single `jr $ra` at
`0x800455C0`. The `beq *0x80130B70 == 0xA` delay slot
`sw $zero, 0x6FC4` executes on every entry. Type
`0xA` then skips `allocAndInitGridCellArray` and the
`n*24` malloc; both arms still `jal load_level_hmp`.

`load_level_hmp` is `0x80043D74`..`0x80044720`,
frame `-0x88`. One generated `jal 0x80043D74`
(`loadLevelAssets` `0x80045464`). Zero
`LOOKUP_FUNC(0x80043D74)`. Single `jr $ra` at
`0x8004471C`. The `rs_malloc` sites use flags-0
(`$a1 = 0`).

`allocAndInitDoublyLinkedNodePool12` is `0x80041EF0`..
`0x80041FA0`, frame `-0x20`. One generated `jal
0x80041EF0` (`load_level_hmp` `0x80044554`, first of
the two-iter `$s5` walk). Zero `LOOKUP_FUNC(0x80041EF0)`.
Single `jr $ra` at `0x80041F9C`. The `rs_malloc` at
`0x80041F14` uses flags-0. The store at `0x80041F24`
is the delay slot of `blez $s1` and also the
fallthrough, so it executes on every entry.

## Object identity

### `0x80136FC4` — HMP asset malloc

Sequence in `load_level_hmp`:

1. `sprintf_recomp` builds a name at `$sp+0x18`.
2. `get_asset_size_extra` (`0x80004D5C`) of that name
   into `$s2`.
3. `rs_malloc($s2, 0)` at `0x80043DD8`.
4. `sw $v0, 0x6FC4($s1)` at `0x80043DF8`
   (`$s1 = lui 0x8013`). This is the only original
   heap-pointer store of the word. `loadLevelAssets`
   zeros the word first; teardown NULLs it after
   the free.
5. DMA via `0x80004AAC` / `0x80004E70` / `0x80004C70`
   into that buffer. Interior `0x1C`/`0x20` are
   relocated in-buffer (`addu` of the buffer base);
   `sw $v0, 0x6DC0` / `sw $v0, 0x4(0x80136DC0)`
   publish those interior pointers as descriptor
   fields, not a second heap pointer.

`$fp` is incoming `$a1` (`0x80136F80`) until
`0x80044278` (`jal 0x80046310` delay slot
`addu $fp, $v0` with `$v0 = lui 0x8013`). Later
`0x6FC4($fp)` loads are this word used as a table
base (`0x20($buf)` walk). They are not `$a0` of a
`jal rs_free`.

`computeGridTileEdgeAdjacencyMasks` loads this word
as a table base, mallocs a scratch of
`lhu 0x18($v0)`, fills it, and `rs_free`s that
scratch at `0x800453AC`. Overlay duplicate
`static_3_80045024` in `funcs_49.c` is the same
consumer. That scratch is not this pointer.

### `0x80136DC8` — `0x8(0x80136DC0)`, W*H halfword grid

`$s0 = 0x80136DC0`. Size = `(lhu +0x38 * lhu +0x3A) << 1`.
`rs_malloc(W*H*2, 0)` at `0x800440A0`. Delay-slot
`sw $v0, 0x8($s0)` at `0x800440C0` executes even when
`W*H <= 0`. When `W*H > 0` a walk writes `0xFFFF`
halfwords into the buffer. `lw $v1, 0x8($a0)` in that
walk is a table-base load, not a second pointer.

No other original `sw` of `0x8($reg)` uses this base.
NPC `0x8` stores, node-pool `sw $zero, 0x8($v0)`
(interior slot `+0x8` of the `0x12`-byte `0x80136FCC`
nodes), and `streamTerrainGridCellsByDistance`
`0xC($s0)` (interior of the `n*24` `0x80136E1C`
records) are different identities.

### `0x80136DCC` — `0xC(0x80136DC0)`, second named asset

`sprintf_recomp` / `get_asset_size_extra` into `$s2`.
`rs_malloc($s2, 0)` at `0x800441AC`.
`sw $v0, 0xC($s1)` at `0x800441D0`
(`$s1 = 0x80136DC0`). DMA dest is that same word.
`lw $v1, 0xC($a2)` at `0x80044230` fills `0xFFFF`
halfwords at stride 4. `processGridCellByDistance`
`lw $v0, 0x6DCC($v0)` at `0x800490B0` (`$v0 = lui
0x8013`) loads it as a table base and does not
`jal rs_free`.

### `0x80136FCC` — 12-byte node-pool malloc

`allocAndInitDoublyLinkedNodePool12`: size =
`n*12` (`$s1<<1 + $s1 << 2`). `rs_malloc(n*12, 0)`
at `0x80041F14`. `sw $v0, 0x6FCC($s0)` at
`0x80041F24` (`$s0 = lui 0x8013`). Incoming `$a0`
is `0x50($sp) + lhu 0x80130C4C + $v0` from
`0x8006B694` on the first `$s5==0` pass of
`load_level_hmp`. Walk writes prev/next halfwords
and zeros each node's `+0x8`. Header halfwords
`0x80136FC8` / `0x80136FC0` are indices, not this
pointer.

Consumers in `funcs_10.c` (`updateActiveGridCellState`,
`getGridCellValueAt`, `buildGridCellMesh`,
`getGridCellFromWorldPos`, and the other `0x6FCC`
table-base loads) index the pool at stride 12 and
do not `jal rs_free`. `funcs_33.c` `0x6FCC` is
`lui 0x800A` / `addiu 0x6FCC` (`0x800A6FCC`).

### `0x80136E1C` — `loadLevelAssets` `n*24` malloc

After `allocAndInitGridCellArray` (skipped on type
`0xA`): size = `n*24` (`$s0<<1 + $s0 << 3`).
`rs_malloc(n*24, 0)` at `0x80045444`.
`sw $v0, 0x6E1C($v1)` at `0x80045450`
(`$v1 = lui 0x8013`). Only original store.

`streamTerrainGridCellsByDistance` `lw $v0, 0x6E1C`
at `0x80042DC8` uses it as a table base (stride
`0x18`); interior `0xC`/`0x10`/`0x14` stores die
with the buffer. `funcs_37.c` `lwc1 0x6E1C($at)`
is `lui 0x800A` rodata.

Incoming `$a0` of `loadLevelAssets` is a count, not
a heap pointer (s3640):

| Caller | PC | `$a0` |
|---|---|---|
| `initMission` | `0x800FA56C` | `getLevelExpansionMemoryBudget` (`0x800` or a computed budget) |
| `setupCutsceneLevel` | `0x800A6D3C` | `lhu` from `0x800B090C[$s0]` |

Neither caller holds a buffer across the call. A
second `loadLevelAssets` without teardown overwrites
these five words and leaks the previous publish.
That is not a second pointer source.

### Descriptor `0x80136DC0` — not a sixth free

`0x0`/`+0x4` are interior HMP pointers. `+0x10`..`+0x3C`
are header floats/halfwords copied from the HMP.
`initGridLayerFromLevelData` (`0x800457D0`) takes
`0x80136DC0` as `$a0` and does not `jal rs_free`.
`funcs_16.c` / `funcs_10.c` `0x6DC0` loads are that
descriptor / its `+0x0` table base. `funcs_37.c` /
`funcs_32.c` `0x6DC0`/`0x6DC8`/`0x6DCC` are
`lui 0x800A` rodata.

## Pairing

Type `0xA` skips the `n*24` malloc of `0x80136E1C`
and the `0x6FCC` / `0x6E1C` / worker / cell frees.
`load_level_hmp` still runs, so `0x80136FC4` /
`0x80136DC8` / `0x80136DCC` / `0x80136FCC` are still
published. Teardown still frees the first three when
`0x80136FC4 != 0` (and NULLs that word). Type `0xA`
therefore leaks the node-pool word; that is not a
second pointer source and is not an unmatched free.
`0x80136E1C` is a paired skip: type `0xA` never
publishes it and never frees it. A type change
between load and teardown can leak or `rs_free`
BSS-zero; `rs_free` itself `beq $s0, $zero` and
returns. That is not a second pointer source.

One generated destructor (`teardownAnimatedMapGridLayer`):

| Wrapper | PC | Route |
|---|---|---|
| `endMissionCleanup` | `0x800FBAB4` | `mainGameLoop` `0x8003E2C4` and `0x8003E388` via `LOOKUP_FUNC(0x800FB9E4)` |
| `cinematicShutdownAudioAndAssets` | `0x800AF270` | `cinematicLoopBody` `0x800A64EC` |

Those two wrappers are the matching destructors of
the two `loadLevelAssets` callers (mission vs
cinematic). The two `mainGameLoop` arms are mutually
exclusive (same pairing as s3624 / s3629 / s3638 /
s3640 / s3641). Sequential double-free of
`0x80136DC8` / `0x80136DCC` is blocked by the
`0x80136FC4` NULL gate; sequential double-free of
`0x80136FCC` / `0x80136E1C` is blocked by that
caller pairing.

Zero `LOOKUP_FUNC` of `0x80041EF0`, `0x80043D74`,
`0x800453C8`, or `0x80045708`. Failed malloc
(`$v0 == 0`) still stores 0 and reaches `rs_free`,
which skips. Interior fills would dereference the
pointer first. That is the same unproven
allocator-failure edge s3604–s3641 left open.

These five words are not the s3636 overlay `0x1C` /
`0x20` writer.

## Classification

The only `jal rs_free` sites that can receive these
pointers are `0x80045730` / `0x8004573C` /
`0x80045748` / `0x80045780` / `0x80045790`. The
only original heap-pointer writers are the five
flags-0 `rs_malloc` stores: HMP asset at
`0x80043DF8`, W*H grid at `0x800440C0`, second
asset at `0x800441D0`, node pool at `0x80041F24`,
and `n*24` at `0x80045450`. Interior HMP / node /
`n*24`-record fields, descriptor `0x80136DC0`
`+0x0`/`+0x4`, the adjacency scratch `$s1`,
worker/cell buffers (closed s3640–s3641), and all
consumer table-base loads are not a second pointer
source. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: five
pointer identities and one allocator store each.

No guard was added. Runtime allocator state remains
unproven. The s3636 overlay skip-path NULL store was
not landed: these words are not that writer.

## Next remaining `jal rs_free`

The next remaining original site in `funcs_9.c` is
`computeGridTileEdgeAdjacencyMasks` `0x800453AC`
(`$a0` = `$s1`, the `lhu 0x18(*0x80136FC4)`
scratch). Then `freeNpcBurstSpawnerTables`
`0x80041B58` / `0x80041B68` / `0x80041B78`,
`destroyNpcContextArrays` `0x8003FE28` /
`0x8003FE50` / `0x8003FE6C` / `0x8003FE78`, and
`freeNpcSlotArray` `0x8003FC0C`.
