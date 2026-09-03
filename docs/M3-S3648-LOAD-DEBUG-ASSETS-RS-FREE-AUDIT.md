# M3 s3648 — loadDebugAssets rs_free of $s0

## Work unit

Static census of `loadDebugAssets` `jal rs_free`
at `0x80024824` (`$a0` = `$s0` rebound at
`0x80024768` to `get_asset_size_extra`
`rs_malloc` at `0x80024750` with `$a1 = 8`).
Enumerated every original load/store of that
`$s0` (including the matching malloc, the ROM
string that occupies `$s0` before the rebind,
DMA-dest and interior descriptor uses, and
whether any caller holds the buffer) and every
`jal rs_free` that can receive that pointer.
`$s0` / DMA-dest loads were classified as
consumers or as a second free. No build or
runtime run was performed.

The discriminator was the single complete
original census of that `jal rs_free` site plus
every original `lw`/`sw`/`addu` of
`loadDebugAssets` `$s0` that can become this
`$a0`, and every `jal rs_free` that can receive
that pointer. No overlay duplicate of
`loadDebugAssets` / `0x800246E8` exists.

- H-NextClassGap: a remaining free can pass a
  pointer that is not the matching allocator
  store, or can free it after a sibling already
  released it without a NULL.
- H-NextClassComplete: every remaining free is
  a destructor of a matching init store, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object
  identities or unshared writers prevent a
  complete classification of a pointer source.

Closed classes were not repeated:
reinsertNpcIntoSortedFreeList `0x4($npc)`,
freeNpcSlotArray `*0x80130BB0`,
destroyNpcContextArrays `*0x80130BC0`/`*0x80130BC4`/
`*0x80130BBC`/`*0x80130BB8`, freeNpcBurstSpawnerTables
`*0x80130BD0`/`*0x80130C08`/`*0x80130C04`,
computeGridTileEdgeAdjacencyMasks `$s1`,
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
same writer as this `$s0`.

## Census size

Original `jal 0x80001C98` in `funcs_7.c`: 1
site. It is this class (`0x80024824`).
`funcs_7.c` `jal rs_free` is exhausted.

`loadDebugAssets` is `0x800246E8`..`0x80024874`,
frame `-0x90`. Two generated `jal 0x800246E8`
(`mainBootstrapWorker` `0x80000C98`,
`advanceVideoFrame` `0x80018428`). Zero
`LOOKUP_FUNC(0x800246E8)`. Zero `lui`/`addiu`
function-pointer constructions of `0x800246E8`.
One overlay-table entry (rom offset `0x242A8`,
size `0x190`); not a second generated body.
Single `jr $ra` at `0x80024870`.
`data_gap_80024878` is an 8-byte gap, not a
clone. No `static_*` clone of these PCs.

The only original skip of both the malloc and
the free is `findManifestEntryByName == -1`
(`beq $s4, -1, L_80024854`). After a live
malloc, the body is straight-line through DMA,
register, and `rs_free`.

## `$s0` accesses

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x8002470C` | `sw $s0, 0x78($sp)` | callee-save | caller's `$s0`; before any rebind |
| string | `0x80024738`/`0x8002473C` | `lui`/`addiu $s0, 0x80000A48` | `$s0` | ROM name for `get_asset_size_extra`; after the `-1` skip |
| size extra | `0x80024744` | `addu $a1, $s0` | `$s0` | still the ROM string |
| find extra | `0x80024764` | `addu $a3, $s0` | `$s0` | still the ROM string |
| DMA malloc | `0x80024750`/`0x80024768` | `jal rs_malloc($s2, 8)`; `addu $s0, $v0` | `$s0` | only original heap-pointer writer |
| DMA dest | `0x80024790` | `sw $s0, 0x14($sp)` | extra arg | dest of `setupAssetDma`; stack only |
| interior | `0x800247A0`/`0x800247A8` | `addiu $v0, $s0, 0x3C` / `+0xC` | stack `0x40`/`0x60($sp)` | pixel / header interiors; not a store of `$s0` |
| header fields | `0x800247BC`/`0x800247C4`/`0x800247D8` | `lhu 0x4` / `lhu 0x6` / `lbu 0x0` | from the buffer | copied onto the stack descriptor |
| DMA free | `0x80024824`/`0x80024828` | `jal rs_free`; `addu $a0, $s0` | `$s0` | destructor; no NULL skip; no post-free NULL |
| restore | `0x80024868` | `lw $s0, 0x78($sp)` | caller's `$s0` | after the free |

`$s0` is never stored to a global. Incoming `$a0`
is `$s3` (asset-system context from
`0x8010E008`), not this buffer. Return is not
`$s0`: the last `$v0` published is immediates
`0x28` / `0x10` at `0x8012BF2A` / `0x8012BF2C`
and the ready byte `1` at `0x80128F20`.

## Object identity

### Incoming `$a0` / `$s3` — context, not this pointer

`$s3` is `$a0`. Both generated callers pass
`*0x8010E008`, not a heap buffer:

| Caller | PC | `$a0` | Skip |
|---|---|---|---|
| `mainBootstrapWorker` | `0x80000C98` | `0x0($s2)` also stored at `0x8010E008` | none |
| `advanceVideoFrame` | `0x80018428` | `*0x8010E008` | two `beq $v0, $zero` gates before the jal |

`$s3` is the DMA context for
`findAssetAcrossSegments` / `setupAssetDma` /
`teardownAssetDma`. Neither caller holds `$s0`
across the call. This incoming `$a0` is not the
`$a0` of the free.

### ROM string at `0x80000A48` — discarded before the free

`$s0` is first `0x80000A48`, used as `$a1` of
`get_asset_size_extra` and `$a3` of
`findAssetAcrossSegments`. `addu $s0, $v0` at
`0x80024768` overwrites it with the malloc
return before that jal. The `-1` skip jumps to
the epilogue before the string lui, so the free
never sees `0x80000A48`. Manifest name
`0x80000A3C` lives in `$s4`.

### `$s0` after `0x80024768` — DMA scratch

Sequence:

1. `findManifestEntryByName(0x80000A3C)` into
   `$s4`. `-1` skips malloc and free.
2. `get_asset_size_extra($s4, 0x80000A48)` into
   `$s2`.
3. `rs_malloc($s2, 8)` into `$s0`. Flags `8` is
   the heap-search qualifier (`andi $s3, 0x88`
   compared to `8` inside `rs_malloc`); it is
   not flags-4 (bit `0x4` selects the other
   heap head). There is no flags-4 retry and no
   original NULL check.
4. `setupAssetDma` extra `0x14($sp) = $s0` is
   the DMA dest; the callee writes that word to
   slot `+0x24` at `0x80111100+index*0x28`.
   `teardownAssetDma` does not `jal rs_free`
   of `+0x24`. No generated `jal rs_free` loads
   that slot word as this `$s0`.
5. Stack descriptor at `$sp+0x40`: `+0x0 =
   $s0+0x3C`, `+0x20 = $s0+0xC`, `+0x24 =
   0x80000A54`, width/height from `lhu
   0x4/0x6($s0)`, format `lbu 0x0($s0)|0x4000`.
   `registerHmtTextureInTable($sp+0x18,
   $sp+0x40, 1)` copies `$t0`/`$t1` into
   `parseHmtMaterials`, which reads those
   header fields and calls
   `loadTextureToMemory` with interior
   `+0x20`/`+0x24`/`+0x30`. Neither callee has
   a `jal rs_free` or `jal rs_malloc`.
   `parseHmtMaterials` stores dest descriptor
   floats/zeros and a texture-id halfword, not
   `$s0`. Return is that halfword, published at
   `0x80128F22`. Same copy-consumer contract as
   s3626/s3637/s3639.
6. `rs_free($s0)`. No NULL skip. No post-free
   NULL.

Interior `+0x0/+0x4/+0x6/+0xC/+0x3C` die with
the buffer. `findAssetAcrossSegments`,
`setupAssetDma`, `teardownAssetDma`, and
`registerHmtTextureInTable` preserve
callee-saved `$s0`. No `jal` between
`addu $s0, $v0` and `rs_free` overwrites `$s0`.

Ready byte `0x80128F20` and debug halfwords
`0x8012BF28`/`0x8012BF2A`/`0x8012BF2C` are not
this pointer. `drawDebugTextString` loads
`0x80128F22` as a texture-id halfword.

Failed malloc (`$s0 == 0`) still reaches
`rs_free`, which skips. The header loads and
DMA dest would dereference `$s0` first. That
is the same unproven allocator-failure edge
s3604–s3647 left open.

This `$s0` is not the s3636 overlay `0x1C`/`0x20`
writer.

### Caller-side stores

Two generated callers; neither receives `$s0`:

| Caller | `$v0` store | Frees `$s0`? |
|---|---|---|
| `mainBootstrapWorker` | none; next is a heap-size subtract | no |
| `advanceVideoFrame` | none; next `addiu $v0, 1` then epilogue | no |

A second `loadDebugAssets` mallocs, DMAs,
registers, and frees a new buffer; the previous
buffer is already freed at the first return.
The `advanceVideoFrame` skip-when-zero arms
never enter this function.

## Pairing

One generated destructor. The `-1` skip is
paired (no malloc). There is no second
`jal rs_free` of this `$s0`. Sequential
double-free would require a caller or callee
to hold `$s0`; no such store exists. Runtime
allocator legitimacy and whether every call's
malloc succeeds remain unproven.

## Classification

The only `jal rs_free` site that can receive
this pointer is `0x80024824`. The only original
heap-pointer writer of `$s0` is the flags-8
malloc at `0x80024768`. Incoming `$s3`, the
ROM string, DMA slot `+0x24`, interior
descriptor pointers, the texture-id halfword
at `0x80128F22`, and the ready/debug
halfwords are not a second pointer source.
This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: one
scratch-buffer identity and one allocator
store of that register.

No guard was added. Runtime allocator state
remains unproven. The s3636 overlay skip-path
NULL store was not landed: this `$s0` is not
that writer.

## Next remaining `jal rs_free`

`funcs_7.c` is exhausted. The next remaining
original site is in `funcs_6.c`:
`destroyTextureLUTs` `0x8001E344` (`$a0` =
`*0x80128F08`), with sibling free of
`*0x80128EFC` at `0x8001E354`.
`uploadTextureDescriptorData` `0x800232CC`
(`$a0` = `$s1`) remains after that.
