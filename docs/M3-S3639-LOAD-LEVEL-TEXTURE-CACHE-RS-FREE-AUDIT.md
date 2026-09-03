# M3 s3639 — loadLevelTextureCache rs_free of $s0

## Work unit

Static census of `loadLevelTextureCache` `jal rs_free`
at `0x80048378` (`$a0` = `$s0` rebound at `0x80048248`
to `rs_malloc(0x136C, 0)` at `0x80048240`). Enumerated
every original load/store of that `$s0` (including the
incoming `$a0` before the rebind, every later store that
can become this `$a0`, and whether any caller holds the
buffer) and every `jal rs_free` that can receive that
pointer. No build or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of `$s0` in `loadLevelTextureCache` and every caller-side
store that can become this `$a0`, and every `jal rs_free`
that can receive that pointer:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeLevelDatBuffers
`*0x801375D0`/`*0x801375D8`/`*0x801375F4`,
load_full_header_image `$s1`,
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
identifies that same writer as this `$s0`.

## Census size

Original `jal 0x80001C98` in `funcs_10.c`: 9 sites. One is
this class (`0x80048378`). Three are `freeLevelDatBuffers`
(closed s3638). The other five are `freeGridCellBuffers`
`0x8004956C`/`0x8004957C`/`0x8004958C`/`0x8004959C`
(`0x80137A5C` / `0x80137A54` / `0x80137A4C` /
`0x80137A68`) and `teardownGridLayerWorker` `0x800495C0`
(`0x80137614`). None of those eight loads this `$s0`.

`loadLevelTextureCache` is `0x80048104`..`0x80048430`,
frame `-0x38`. Two generated `jal 0x80048104`; zero
`LOOKUP_FUNC(0x80048104)`; zero `lui`/`addiu` function-
pointer constructions of `0x80048104` (the only `0x8104`
immediate is `lui $zero, 0x8104` in `funcs_27.c`, which
does not build this address). Single `jr $ra` at
`0x8004842C`. No original branch skips the `0x136C`
malloc or the free. The register loop at `0x80048320` is
skipped when `*0x80137A44 <= 5`, but that arm still
falls into `L_80048378`.

A host PATCH at `0x80048248` (s620) jumps to the epilogue
when the malloc return is outside KSEG0. That skip is not
original and is not this work unit.

Original `$s0` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x80048108` | `sw $s0, 0x18($sp)` | callee-save | caller's `$s0`; before any rebind |
| incoming | `0x8004810C` | `addu $s0, $a0` | `$s0` | reserved-size constant, not a heap pointer |
| count math | `0x80048138` | `subu $v0, $v0, $s0` | `$s0` | `getLoadedTextureCount` minus reserved |
| count base | `0x80048148` | `lui $s0, 0x8013` | `$s0` | first rebind; not a heap pointer |
| count store | `0x80048168`/`0x80048170` | `sw/lw 0x7A44($s0)` | `0x80137A44` | extra-slot count; then `$s0` unused until malloc |
| DMA malloc | `0x80048240`/`0x80048248` | `jal rs_malloc(0x136C, 0)`; `addu $s0, $v0` | `$s0` | only original heap-pointer writer; flags-0 |
| fill bases | `0x8004824C`..`0x8004827C` | `addu $v0/$a0/$v1/$a1, $s0, …` | interior | palette at `+0x58`, RGB at `+0x1058` |
| header fields | `0x800482B8`..`0x80048308` | `sb`/`sh`/`sw`/`swc1` of immediates and `$s0+off` | into the buffer | `+0x0/+0x20/+0x24` are interior self-pointers |
| name | `0x80048320` | `addiu $a0, $s0, 0x48` | stack dest | `sprintf` into the buffer |
| register | `0x80048330`/`0x80048334` | `addiu $a0, $s0, 0x34`; `addu $a1, $s0` | callee args | descriptor / header; not a store of `$s0` |
| DMA free | `0x80048378`/`0x8004837C` | `jal rs_free`; `addu $a0, $s0` | `$s0` | destructor; no NULL skip; no post-free NULL |
| restore | `0x80048428` | `lw $s0, 0x18($sp)` | caller's `$s0` | after the free |

`$s0` is never stored to a global. After the free, `$s0`
is not an argument to `findAssetAcrossSegments`,
`registerServiceWorker`, or `startServiceWorker`. Return
is whatever `getLoadedTextureCount` last returned, not
`$s0`.

## Object identity

### Incoming `$a0` — reserved-size constant, discarded

`$s0` is first `$a0`. Both generated callers pass an
immediate, not a heap pointer:

| Caller | PC | `$a0` | Skip |
|---|---|---|---|
| `initMission` | `0x800FA67C` | `0x1000` | `*0x80130B70 == 0xA` |
| `load_cutscene` | `0x800A688C` | `0x5DC0` | cutscene-type byte `== 0xA` |

`getLoadedTextureCount` (`0x80023950`) returns
`*0x8011A7D0 - *0x8011A7D8`. The body subtracts `$s0`
and converts that remainder into an extra-slot count
stored at `0x80137A44`. `lui $s0, 0x8013` then overwrites
the reserved-size value. Neither caller holds a buffer
across the call. This incoming `$a0` is not the `$a0` of
the free.

### Count-table malloc at `0x80137614` — different identity

`rs_malloc` at `0x80048164` (flags-0, size =
`count * 12`) is stored at `0x80137614` in the delay
slot of that jal. `$s0` is only the `0x8013` lui-base
for the count word. That table pointer is the
`teardownGridLayerWorker` word, not this `$s0`. The
register loop writes texture-id halfwords into
`0x80137614 + 0x3C + i*0xC` (`+0x4`, `+0x6`, `+0x8`).
Those halfwords are not this pointer.

### `$s0` after `0x80048248` — packed 0x136C scratch

Sequence:

1. `rs_malloc(0x136C, 0)` into `$s0`. There is no
   flags-4 retry and no original NULL check.
2. A descending fill writes 0x1000 bytes of index values
   at `$s0+0x58`. A 256-iter stride-3 fill writes an RGB
   ramp at `$s0+0x1058`.
3. Header words in the same buffer: `+0x0 = $s0+0x58`,
   `+0x20 = $s0+0x1058`, `+0x24 = $s0+0x48`,
   `+0x28/+0x2A = 0x40`, `+0x2C = 1`, `+0x2E = 0x20`,
   `+0x40 = 0`, `+0x44 = 1`, plus two rodata floats at
   `+0x38/+0x3C`. Descriptor at `+0x34` is `sh 1` plus
   those floats/zero/flag (same 0x14-byte layout as
   s3637's stack descriptor).
4. When `*0x80137A44 > 5`, a loop from index 5
   `sprintf`s a name at `$s0+0x48`, then
   `registerHmtTextureInTable($s0+0x34, $s0, 0)`.
   That wrapper copies `$t0`/`$t1` into
   `parseHmtMaterials`, which reads header fields and
   calls `loadTextureToMemory` with interior
   `+0x20`/`+0x24`/`+0x30`. It has no `jal rs_free`.
   `sw $a2, 0xC($v0)` inside `parseHmtMaterials` stores
   descriptor `+0x10` (the `sb 1` flag word), not `$s0`.
   Return is a texture-id halfword published into the
   `0x80137614` table, then `getTextureAttrBySlot` of
   that id. Same copy-consumer contract as s3626/s3637.
5. `rs_free($s0)`. No NULL skip. No post-free NULL.

Interior `+0x0/+0x20/+0x24` die with the buffer.
`sprintf`, `registerHmtTextureInTable`, and
`getTextureAttrBySlot` preserve callee-saved `$s0`.
No `jal` between `addu $s0, $v0` and `rs_free`
overwrites `$s0`.

Failed malloc (`$s0 == 0`) still reaches `rs_free`,
which skips. The fill loops would dereference `$s0`
first. That is the same unproven allocator-failure
edge s3604–s3638 left open.

This `$s0` is not the s3636 overlay `0x1C`/`0x20`
writer.

### Caller-side stores

Two generated callers; neither receives `$s0`:

| Caller | `$v0` store | Frees `$s0`? |
|---|---|---|
| `initMission` | none; next is epilogue | no |
| `load_cutscene` | none; next `initCutsceneAudioChannels($s3)` | no |

A second `loadLevelTextureCache` mallocs, fills,
registers, and frees a new buffer; the previous buffer
is already freed at the first return. The skip-when-
type-`0xA` arms never enter this function.

## Pairing

One generated destructor. Both the register-loop arm and
the `*0x80137A44 <= 5` skip reach it. There is no second
`jal rs_free` of this `$s0`. Sequential double-free would
require a caller or callee to hold `$s0`; no such store
exists. Runtime allocator legitimacy and whether every
call's malloc succeeds remain unproven.

## Classification

The only `jal rs_free` site that can receive this pointer
is `0x80048378`. The only original heap-pointer writer of
`$s0` is the flags-0 malloc at `0x80048248`. Incoming
`$a0`, the `0x8013` lui-base, the `0x80137614` count
table, interior self-pointers, the texture-id halfwords,
and the callee copy of descriptor `+0x10` are not a
second pointer source. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: one scratch-
buffer identity and one allocator store of that register.

No guard was added. Runtime allocator state remains
unproven. The s3636 overlay skip-path NULL store was not
landed: this `$s0` is not that writer. The existing s620
host malloc-range jump is unchanged.

## Next remaining `jal rs_free`

The next remaining original site in `funcs_10.c` is
`freeGridCellBuffers` `0x8004956C` (`$a0` =
`*0x80137A5C`), with sibling frees of `*0x80137A54` at
`0x8004957C`, `*0x80137A4C` at `0x8004958C`, and
`*0x80137A68` at `0x8004959C`. `teardownGridLayerWorker`
`0x800495C0` (`*0x80137614`) remains after that.
