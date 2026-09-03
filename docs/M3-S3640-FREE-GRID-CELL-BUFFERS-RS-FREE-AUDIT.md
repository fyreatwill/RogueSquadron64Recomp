# M3 s3640 — freeGridCellBuffers rs_free of *0x80137A5C / *0x80137A54 / *0x80137A4C / *0x80137A68

## Work unit

Static census of `freeGridCellBuffers` `jal rs_free` at
`0x8004956C` (`$a0` = `*0x80137A5C`), plus the sibling
frees of `*0x80137A54` at `0x8004957C`, `*0x80137A4C`
at `0x8004958C`, and `*0x80137A68` at `0x8004959C`.
Enumerated every original load/store of those four words
(including the matching `rs_malloc` in
`allocAndInitGridCellArray`, every later store that can
become these `$a0`s, and whether any caller holds the
buffers) and every `jal rs_free` that can receive those
pointers. No build or runtime run was performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original `lw`/`sw`/`addu`
of `0x80137A5C` / `0x80137A54` / `0x80137A4C` /
`0x80137A68` and every caller-side store that can become
these `$a0`s, and every `jal rs_free` that can receive
those pointers:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadLevelTextureCache `$s0`
0x136C scratch, freeLevelDatBuffers `*0x801375D0`/`*0x801375D8`/
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
identifies that same writer as one of these four words.
`teardownGridLayerWorker` `*0x80137614` is a different
identity (the `loadLevelTextureCache` count-table malloc).

## Census size

Original `jal 0x80001C98` in `funcs_10.c`: 9 sites. Four are
this class (`0x8004956C` / `0x8004957C` / `0x8004958C` /
`0x8004959C`). Three are `freeLevelDatBuffers` (closed
s3638). One is `loadLevelTextureCache` (closed s3639). The
remaining site is `teardownGridLayerWorker` `0x800495C0`
(`*0x80137614`). None of those five loads these four words.

`freeGridCellBuffers` is `0x8004955C`..`0x800495AC`,
frame `-0x18`. One generated `jal 0x8004955C`
(`teardownAnimatedMapGridLayer` `0x80045770`). Zero
`LOOKUP_FUNC(0x8004955C)`; zero `lui`/`addiu`
function-pointer constructions of `0x8004955C`. Single
`jr $ra` at `0x800495A8`. The body is straight-line: no
original branch skips any of the four frees. No NULL skip
and no post-free NULL.

`allocAndInitGridCellArray` is `0x80047E50`..`0x80048100`,
frame `-0x20`. One generated `jal 0x80047E50`
(`loadLevelAssets` `0x80045430`). Zero
`LOOKUP_FUNC(0x80047E50)`; zero `lui`/`addiu`
function-pointer constructions of `0x80047E50`. Single
`jr $ra` at `0x800480FC`. All four `rs_malloc` calls use
flags-0 (`$a1 = 0`). All four stores execute on every
entry; the `blez $s1` and `5 < $s1` branches skip only
interior fills.

Coincidental `lwc1` of `0x7A54($at)` / `-0x7A5C($at)` /
`-0x7A54($at)` / `-0x7A4C($at)` / `-0x7A68($at)` in
`npcWingmanUpdate` / `npcGroundTroopUpdate` /
`playAttachmentCueNoTexture` / `applyCraftAnimDetailParamsB`
use `$at` = `lui 0x800A` or `lui 0x800B` (rodata floats),
not these words.

## Object identity

### `0x80137A5C` — cell-array malloc, stride 0xB8

Sequence in `allocAndInitGridCellArray`:

1. Size = `$s1 * 0xB8` (`n*2 + n << 3 - n << 3`).
2. `rs_malloc(n*0xB8, 0)` at `0x80047E78`.
3. Delay-slot-adjacent `sw $a0, 0x7A5C($v1)` at
   `0x80047E90` (`$a0` = `$v0`, `$v1` = `lui 0x8013`).
   This is the only original store of the word.

When `n > 0`, a walk writes cell index halfwords at
`+0x16` with stride 0xB8. When `n > 5`, a second walk
from index 5 writes neighbor halfwords and interior
self-pointers at `base + i*0xB8 + 0x398`. Those stores
are into the buffer, not a second heap pointer.

Consumers load the word as the cell-array base and add
`index * 0xB8`. None `jal rs_free`.

### `0x80137A54` — `12*(10n+1)` table malloc

`rs_malloc(12*(10n+1), 0)` at `0x8004801C`;
`sw $v0, 0x7A54($v1)` at `0x80048030` (`lui 0x8013`).
Only original store. Consumers (`emitGridCellTileStrip*`,
`mapCellGeometryToGridSpace`, `buildGridCellMesh`) load
it as a table base. None `jal rs_free`.

### `0x80137A4C` — `n*4` halfword-table malloc

`0x80137A70` holds `n<<1`. `rs_malloc((n<<1)<<1, 0)` =
`rs_malloc(n*4, 0)` at `0x80048034`; `sw $v0, 0x7A4C($v1)`
at `0x8004804C` (delay slot of `blez`, so the store
always runs). When `2n > 0`, a fill writes halfwords
`1, 6, 11, ...` with stride 2. Only original store of
the word. Consumers load it as a table base. None
`jal rs_free`.

### `0x80137A68` — `200*(n/10)` malloc, interior split at `0x80137A6C`

Signed `n/10` (magic `0x66666667`) is stored at
`0x80137A60`. `rs_malloc(200*(n/10), 0)` at
`0x800480BC`; `sw $v0, 0x7A68($a1)` at `0x800480CC`.
Then `addiu $a1, $a1, 0x7A68` takes the address of the
word and `sw $v0+100*(n/10), 0x4($a1)` publishes the
interior split at `0x80137A6C`. That interior word is
not independently freed. The only original store of
`0x80137A68` is the malloc.

`buildVisibleTerrainGridAroundCamera` takes
`&0x80137A68` and loads `0x0($v0)` after
`(flag&1)<<2`, selecting either the malloc base or the
interior split as a table base. Load only; no store of
a new pointer and no `jal rs_free`.

Count words `0x80137A70` / `0x80137A60` / `0x80137A58`
are integers, not heap pointers.

### Incoming `$a0` of `allocAndInitGridCellArray` — cell count, discarded

`$s1` is incoming `$a0`. Both generated callers of
`loadLevelAssets` pass a count, not a heap pointer:

| Caller | PC | `$a0` | Skip |
|---|---|---|---|
| `initMission` | `0x800FA56C` | `getLevelExpansionMemoryBudget` (`0x800` or a computed budget) | `*0x80130B70 == 0xA` |
| `setupCutsceneLevel` | `0x800A6D3C` | `lhu` from `0x800B090C[$s0]` | `*0x80130B70 == 0xA` |

`loadLevelAssets` copies that count into `$s0`, stores it
as a halfword at `0x80130C4C`, then passes it to
`allocAndInitGridCellArray`. Neither caller holds a
buffer across the call.

### Sibling `n*24` malloc at `0x80136E1C` — different identity

After `allocAndInitGridCellArray` returns,
`loadLevelAssets` `rs_malloc(n*24, 0)` stores `$v0` at
`0x80136E1C`. `teardownAnimatedMapGridLayer` frees that
word after `freeGridCellBuffers`. It is not one of these
four pointers. `0x80137614` is the
`loadLevelTextureCache` count table, freed by
`teardownGridLayerWorker` before `freeGridCellBuffers`
in the same wrapper.

## Pairing

`loadLevelAssets` skips `allocAndInitGridCellArray` when
`*0x80130B70 == 0xA`. `teardownAnimatedMapGridLayer`
skips `freeGridCellBuffers` (and the sibling 0x6FCC /
0x6E1C frees) on the same compare. Paired skip: type
`0xA` never publishes these four words and never frees
them. A type change between load and teardown can leak
or `rs_free` BSS-zero; `rs_free` itself
`beq $s0, $zero` and returns. That is not a second
pointer source.

One generated destructor (`freeGridCellBuffers`), reached
from `teardownAnimatedMapGridLayer`:

| Wrapper | PC | Route |
|---|---|---|
| `endMissionCleanup` | `0x800FBAB4` | `mainGameLoop` `0x8003E2C4` and `0x8003E388` via `LOOKUP_FUNC(0x800FB9E4)` |
| `cinematicShutdownAudioAndAssets` | `0x800AF270` | `cinematicLoopBody` `0x800A64EC` |

Those two wrappers are the matching destructors of the
two `loadLevelAssets` callers (mission vs cinematic).
The two `mainGameLoop` arms are mutually exclusive
(same pairing as s3624 / s3629 / s3638). Sequential
double-free of the four words is blocked by that
caller pairing; the destructor does not NULL after
release. A second `loadLevelAssets` without teardown
overwrites the four words and leaks the previous
publish. Neither is a second pointer source for these
four frees.

Zero `LOOKUP_FUNC` of `0x80047E50`, `0x8004955C`,
`0x800453C8`, or `0x80045708`. Failed malloc (`$v0 == 0`)
still stores 0 and reaches `rs_free`, which skips. The
interior fills would dereference the pointer first.
That is the same unproven allocator-failure edge
s3604–s3639 left open.

These four words are not the s3636 overlay `0x1C`/`0x20`
writer.

## Classification

The only `jal rs_free` sites that can receive these
pointers are `0x8004956C` / `0x8004957C` / `0x8004958C` /
`0x8004959C`. The only original heap-pointer writers are
the four flags-0 `rs_malloc` stores in
`allocAndInitGridCellArray`. Interior cell fields, the
`0x80137A6C` split, the `n*24` sibling at `0x80136E1C`,
the `0x80137614` count table, count words, and all
consumer table-base loads are not a second pointer
source. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: four pointer
identities and one allocator store each.

No guard was added. Runtime allocator state remains
unproven. The s3636 overlay skip-path NULL store was not
landed: these words are not that writer.

## Next remaining `jal rs_free`

The next remaining original site in `funcs_10.c` is
`teardownGridLayerWorker` `0x800495C0` (`$a0` =
`*0x80137614`). That word is the matching
`loadLevelTextureCache` `rs_malloc(count*12, 0)` store
at `0x80048180` (s3639). After that site, `funcs_10.c`
`jal rs_free` is exhausted.
