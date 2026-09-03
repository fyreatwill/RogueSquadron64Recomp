# M3 s3637 — load_full_header_image rs_free of $s1

## Work unit

Static census of `load_full_header_image` `jal rs_free`
at `0x800544D8` (`$a0` = `$s1` = matching
`get_asset_size_extra` `rs_malloc` at `0x80054428`,
flags-0; DMA dest then `sh` a halfword at `0x80137C70`
in the delay slot of the free). Enumerated every original
load/store of `$s1` (including the DMA dest, every later
store that can become this `$a0`, and whether any caller
holds the buffer) and every `jal rs_free` that can receive
that pointer. No build or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of `$s1` in `load_full_header_image` and every caller-side
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

Closed classes were not repeated: attachedMeshOverlayNpcHandler
`0x1C`/`0x20` (Gap, s3636; sibling `freeListEntryPointers`
unreferenced), loadAssetIntoNewSlot `$s6`,
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

Original `jal 0x80001C98` in `funcs_11.c`: 7 sites. One is
this class (`0x800544D8`). The other six are
`attachedMeshOverlayNpcHandler` `0x80054344` (`0x1C($s0)`,
Gap, s3636), `freeListEntryPointers` `0x80054620`
(unreferenced sibling of s3636), `loadAssetIntoNewSlot`
`0x800549E4` (closed s3635), `freeAnimationPhasePool`
`0x80054AC8`/`0x80054AEC` (closed s3634), and
`loadAssetAndIterateSubchunks` `0x8005519C` (closed s3633).
None of those six loads this function's `$s1`.

`load_full_header_image` is `0x800543F4`..`0x800544FC`,
frame `-0x58`. Five generated `jal 0x800543F4`; zero
`LOOKUP_FUNC(0x800543F4)`; zero `lui`/`addiu` function-
pointer constructions of `0x800543F4`. Single `jr $ra`
at `0x800544F8`. The body is straight-line: no original
branch skips the malloc or the free.

Original `$s1` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x80054400` | `sw $s1, 0x44($sp)` | callee-save | not a heap store |
| table temp | `0x80054404`/`0x80054408` | `lui $s1, 0x8013`; `lw 0x7CFC($s1)` | `0x80137CFC` | asset-table arg; then overwritten |
| DMA malloc | `0x80054428`/`0x80054444` | `jal rs_malloc($s3, 0)`; `addu $s1, $v0` | `$s1` | only original heap-pointer writer; flags-0 |
| DMA dest | `0x8005446C` | `sw $s1, 0x14($sp)` | stack | `setupAssetDma` dest, not a second pointer |
| convert base | `0x8005447C` | `addiu $s0, $s1, 0x4` | `$s0` | header after 4-byte prefix; never stored |
| flags | `0x800544BC`/`0x800544CC` | `lhu 0x32($s1)`; `ori 0x300`; `sh` | header `+0x32` | into the buffer; not a store of `$s1` |
| DMA free | `0x800544D0`/`0x800544D8` | `addu $a0, $s1`; `jal rs_free` | `$s1` | destructor; no NULL skip; no post-free NULL |
| tex id | `0x800544DC` | `sh $v0, 0x7C70($s0)` | `0x80137C70` | delay-slot of the free; halfword id, not `$s1` |
| return | `0x800544E0` | `lhu $v0, 0x7C70($s0)` | `0x80137C70` | function return is the texture id |
| restore | `0x800544F0` | `lw $s1, 0x44($sp)` | caller's `$s1` | after the free |

`$s1` is never stored to a global. `$v0` is the texture-id
halfword, not `$s1`.

## Object identity

### `$s1` — packed DMA buffer

Sequence:

1. Incoming `$a0` (asset name) is saved in `$s2`.
2. `get_asset_size_extra($a0=0x80137CFC, $a1=name)` into
   `$s3`.
3. `rs_malloc($s3, 0)` into `$s1`. There is no flags-4
   retry and no NULL check.
4. `findAssetAcrossSegments` overwrites `$s2` with the
   asset handle. `setupAssetDma` dest `$s1` /
   `teardownAssetDma` of that handle.
5. `$s0 = $s1+4`. `full_header_image_offset_convert($s0, $s0)`
   relocates eight interior words plus `+0x20`/`+0x24`
   *into* the malloc buffer. It has no `jal rs_malloc` or
   `jal rs_free`.
6. A stack descriptor at `$sp+0x18` is filled (`sh 1`,
   two floats, `sw 0`, `sb 1`). Header `+0x32` is OR'd
   with `0x300`.
7. `registerHmtTextureInTable($sp+0x18, $s1+4, 1)` copies
   pixels and publishes a texture-id halfword. It does not
   store `$s1` or `$s1+4`, and it has no `jal rs_free`
   (same copy-consumer contract as s3626).
8. `rs_free($s1)`. Delay slot stores the texture id at
   `0x80137C70`. Return is that halfword.

`$s0` is only a `+4` alias of `$s1`. Interior convert
stores die with the buffer. `0x14($sp)` is the DMA dest
argument; it is not re-loaded. `setupAssetDma` holds dest
in a command slot until `teardownAssetDma` completes,
which is before this free (same dest-slot contract as
s3612/s3627/s3633/s3635). Failed malloc (`$s1==0`) still
reaches `rs_free`, which `beq $s0, $zero` and returns;
the convert walk would dereference `$s1+4` first. That
is the same unproven allocator-failure edge s3604–s3635
left open.

No `jal` clobbers `$s1` between `addu $s1, $v0` and
`rs_free`: `findAssetAcrossSegments`, `setupAssetDma`,
`teardownAssetDma`, `full_header_image_offset_convert`,
and `registerHmtTextureInTable` preserve callee-saved
`$s1`.

### `0x80137C70` — texture-id halfword, not this pointer

The only original store is the delay-slot `sh $v0` at
`0x800544DC`. The only original load of that same word is
the return `lhu` at `0x800544E0` and
`dispatchOverlaySetupByParentAssetName` `lhu $a2, 0x7C70`
at `0x80053D74`, which passes the id to
`setMaterialFlagByIdInMeshTree`. That consumer does not
`jal rs_free` of the halfword or of `$s1`. `funcs_38.c`
`lwc1 0x7C70($at)` is `0x800A7C70` (float constant);
`funcs_39.c` `-0x7C70($at)` is a different address.

This `$s1` is not the s3636 overlay `0x1C`/`0x20` writer.

### Caller-side stores of the return (texture id), not `$s1`

Five generated callers; none receive `$s1`:

| Caller | PC | `$a0` name | `$v0` store | Frees `$s1`? |
|---|---|---|---|---|
| `loadLevelAssets` | `0x80045488` | `$sp+0x10` (`sprintf`) | none; next `lw 0x6FC4($s1)` | no |
| `mallocCraftSelectionData` | `0x800AA19C` | `0x800A5438` | none; next `hangarLoadShadows` | no |
| `initVwingHudAndSlotState` | `0x800B9420` | `0x800A6974` | `sh $v0, 0x800CFA6C` | no |
| `initInteractiveSceneContext` | `0x800C414C` | `0x800A7470` | none; next `initNpcSlotList` | no |
| `runModelViewerLoop` | `0x800C9D54` | `0x800A7920` | none; next `buildModelViewerTextPage` | no |

The `0x800CFA6C` halfword is a texture id, not a heap
pointer. No caller `jal rs_free` of `$v0` or of `$s1`.
A second `load_full_header_image` mallocs, converts,
registers, and frees a new buffer; the previous buffer
is already freed at the first return.

## Pairing

One generated destructor. The straight-line body always
reaches it. There is no second `jal rs_free` of this
`$s1`. Sequential double-free would require a caller to
hold `$s1`; no caller-side store exists. Runtime
allocator legitimacy and whether every call's malloc
succeeds remain unproven.

## Classification

The only `jal rs_free` site that can receive this pointer
is `0x800544D8`. The only original heap-pointer writer of
`$s1` is the flags-0 malloc at `0x80054444`. The `$s0`
`+4` alias, the DMA dest slot, the interior convert
stores, the `0x80137C70` texture-id halfword, and the
caller-side id store are not a second pointer source.
This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope. `H-NextClassUnevaluable` is not
selected: one DMA-buffer identity and one allocator store
of that register.

No guard was added. Runtime allocator state remains
unproven. The s3636 overlay skip-path NULL store was not
landed: this `$s1` is not that writer.

## Next remaining `jal rs_free`

`funcs_11.c` `jal rs_free` is exhausted. `funcs_12.c` is
already exhausted (s3626–s3632). The next remaining
original site is `freeLevelDatBuffers` `0x80047B0C`
(`$a0` = `*0x801375D0`), with sibling frees of
`*0x801375D8` at `0x80047B20` and `0x1C($s0)` at
`0x80047B2C`.
