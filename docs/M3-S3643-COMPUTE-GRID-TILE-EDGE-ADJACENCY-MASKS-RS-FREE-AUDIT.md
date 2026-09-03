# M3 s3643 — computeGridTileEdgeAdjacencyMasks rs_free of $s1

## Work unit

Static census of `computeGridTileEdgeAdjacencyMasks`
`jal rs_free` at `0x800453AC` (`$a0` = `$s1`, the
`rs_malloc(lhu 0x18(*0x80136FC4), 0)` scratch).
Enumerated every original load/store of that `$s1`
(including the matching malloc at `0x80044C00`,
every later store that can become this `$a0`, and
whether any caller holds the buffer) and every
`jal rs_free` that can receive that pointer. No
build or runtime run was performed.

The discriminator was the single complete original
census of that `jal rs_free` site plus every
original `lw`/`sw`/`addu` of this `$s1` and every
caller-side store that can become this `$a0`, and
every `jal rs_free` that can receive that pointer.
The overlay duplicate `static_3_80045024` in
`funcs_49.c` is a second generated body of the
same tail PCs and is included.

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

Closed classes were not repeated: teardownAnimatedMapGridLayer
remaining `*0x80136DC8`/`*0x80136DCC`/`*0x80136FC4`/
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
same writer as this `$s1`.

## Census size

Original `jal 0x80001C98` in `funcs_9.c`: 14 sites.
One is this class (`0x800453AC`). Five are
`teardownAnimatedMapGridLayer` (closed s3642).
Three are `freeNpcBurstSpawnerTables`. Four are
`destroyNpcContextArrays`. One is
`freeNpcSlotArray`. None of those thirteen loads
this `$s1`.

`computeGridTileEdgeAdjacencyMasks` is
`0x80044BE4`..`0x800453C8`, frame `-0x20`.
Section-3 `.text` `FuncEntry` offset `0x447A4`,
`rom_size 0x7E4`. One generated `jal 0x80044BE4`
(`loadLevelAssets` `0x80045598`). Zero
`LOOKUP_FUNC(0x80044BE4)`. Single `jr $ra` at
`0x800453C0`. The only jals in the body are
`rs_malloc` (`0x80044C00`), `rs_memset`
(`0x80044C18` / `0x800078E0`), and `rs_free`
(`0x800453AC`).

`loadLevelAssets` is `0x800453C8`..`0x800455C4`
(closed s3642). Two generated `jal 0x800453C8`;
zero `LOOKUP_FUNC(0x800453C8)`. The adjacency jal
is skipped when `*0x80130B39 != 0` or
`*0x80130B70 == 0x11`. Type `0xA` does not skip
it. Incoming `$a0` of `loadLevelAssets` is a
count, not a heap pointer, and is not passed
through (delay slot is `nop`).

## Object identity

### `$s1` — HMP `+0x18` scratch malloc

Original `$s1` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x80044BF8` | `sw $s1, 0x14($sp)` | callee-save | caller's `$s1`; before any rebind |
| malloc | `0x80044C00` / `0x80044C08` | `jal rs_malloc`; `addu $s1, $v0` | `$s1` | only original heap-pointer writer; flags-0; size = `lhu 0x18(*0x80136FC4)` |
| memset | `0x80044C10` / `0x80044C18` | `addu $a0, $s1`; `jal rs_memset($s1, 0xFF, same size)` | `$s1` | fill, not a store of the pointer |
| tile load | `0x80044C70` | `addu $v0, $s1, (lhu & 0x1FFF)` | interior | `lbu` of one flag byte |
| tile store | `0x80044DA4` / `0x80044DA8` | `addu $v0, $s1, (lhu & 0x1FFF)`; `sb $t1, 0($v0)` | into the buffer | adjacency flags; dies with the scratch |
| second-loop load | `0x80044DF8` | `addu $v0, $s1, $t2` | interior | `lbu` of `$s1[$t2]` |
| free | `0x800453AC` / `0x800453B0` | `jal rs_free`; `addu $a0, $s1` | `$s1` | destructor; no NULL skip; no post-free NULL |
| restore | `0x800453B8` | `lw $s1, 0x14($sp)` | caller's `$s1` | after the free |

`$s1` is never stored to a global. After the
malloc, the only `ctx->r17 =` writes are that
`addu $s1, $v0` and the epilogue restore. The
function does not take a heap pointer: it loads
`*0x80136FC4` as a table base, mallocs a scratch
of `lhu 0x18($v0)`, and frees that scratch.

`0x80136FC4` itself is the HMP asset (closed
s3642) and is not this `$a0`. `*0x80136DC0`
`+0x38`/`+0x3A` are W/H for the first walk.
`*0x80136DC4 + 0x10` is the second-loop record
base (stride `0x1E`); the `MEM_B` stores at
`$a3±n` write interpolated neighbor bytes into
those records, not a second copy of `$s1`.

### Paths to the free

The first walk is skipped when
`lhu 0x3A(0x80136DC0) == 0`. The second walk is
skipped when `lhu 0x18(*0x80136FC4) == 0`
(`beq` to `L_800453AC`). Both skip arms and the
second-loop exit reach the same `jal rs_free`.
No original branch skips the free after the
malloc.

### Overlay duplicate `static_3_80045024`

`funcs_49.c` `static_3_80045024` is the same
instruction stream from `0x80045024` through
`0x800453C4` (fallthrough tail after
`sb 0x2($a3)` at `0x80045020`). It has no
prologue, no malloc, and no `$s1` assignment
except the epilogue restore. It is not in any
`FuncEntry` table. Zero `LOOKUP_FUNC(0x80045024)`.
No `L_80045024` label in the live body.

The only generated `jal 0x80045024` is
`__OSGlobalIntMask` `0x8003C2D8` in `funcs_8.c`.
That function starts at `0x80039110` as INVALID
words and nearby `0x3F800000` / `0x3FAAAAAB`
float constants; the jal is data-as-code, not a
live caller. Reached via the live function,
`$s1` is already the malloc result. This is not
a second destructor or a second pointer source.

## Callers

`loadLevelAssets` is the only generated caller.

| Caller | PC | `$a0` of `loadLevelAssets` |
|---|---|---|
| `initMission` | `0x800FA56C` | `getLevelExpansionMemoryBudget` (`0x800` or a computed budget) |
| `setupCutsceneLevel` | `0x800A6D3C` | `lhu` from `0x800B090C[$s0]` |

Neither holds the adjacency scratch. The s3636
overlay `0x1C`/`0x20` writer is a different
`rs_malloc(0x80, 0)` and is not this `$s1`.

## Verdict

H-NextClassComplete. One matching flags-0
`rs_malloc` store into `$s1`, one destructor,
no caller-held copy, no second live `jal rs_free`
of that pointer. H-NextClassGap is refuted at
static scope. Runtime allocator legitimacy
(including `rs_free` of a NULL malloc return)
remains unproven. No guard was added.
