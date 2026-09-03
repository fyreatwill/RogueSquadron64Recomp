# M3 s3635 — loadAssetIntoNewSlot rs_free of $s6 DMA scratch

## Work unit

Static census of `loadAssetIntoNewSlot` `jal rs_free`
at `0x800549E4` (`$a0` = `$s6` = matching
`get_asset_size_extra` `rs_malloc` at `0x8005489C` /
`0x800548A8`). Enumerated every original load/store of
`$s6` (including the DMA dest slot, the `$s3` walk alias,
the converted-buffer malloc stored at `0x0($s4)`, and
every later store that can become this `$a0`) and every
`jal rs_free` that can receive that pointer. No build or
runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of `$s6` in `loadAssetIntoNewSlot` and every caller-side
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

Closed classes were not repeated: freeAnimationPhasePool
slot `+0x0` / `0x80137C84`, loadAssetAndIterateSubchunks
`$s6`, freeAllHobFiles slot `+0x8`, releaseMeshAsset
`$s5`, load_hmt_and_hob `$s3`/`0x6C`/`0x74`,
freeSubtitleOverlay `*0x80139010`, freeTxtFile globals,
loadSpriteSheetTextureFrames inlined-malloc,
loadAndRelocateAsset load_asset, loadExplosionTextures
load_asset, freeEffectAssetBuffers globals,
loadSkyHorizonHob stack scratch,
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
this class (`0x800549E4`). The other six are
`attachedMeshOverlayNpcHandler` `0x80054344` (`0x1C($s0)`),
`load_full_header_image` `0x800544D8` (`$s1`),
`freeListEntryPointers` `0x80054620` (`0x1C($s0)`),
`freeAnimationPhasePool` `0x80054AC8`/`0x80054AEC`
(closed s3634), and `loadAssetAndIterateSubchunks`
`0x8005519C` (closed s3633). None of those six loads this
function's `$s6`. `loadAssetAndIterateSubchunks`' `$s6` is
a different callee-saved register in a different frame.

`loadAssetIntoNewSlot` is `0x800547C0`..`0x80054A14`,
frame `-0x58`. Twelve generated callers; zero
`LOOKUP_FUNC(0x800547C0)`. Single `jr $ra` at `0x80054A10`.

Original `$s6` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x800547D0` | `sw $s6, 0x50($sp)` | callee-save | not a heap store |
| DMA malloc | `0x8005489C`/`0x800548A8` | `jal rs_malloc($v0, 0)`; `addu $s6, $v0` | `$s6` | only original heap-pointer writer; flags-0 |
| walk alias | `0x800548B4`/`0x80054950` | `addu $s3, $s6` | `$s3` | same pointer; never stored |
| DMA dest | `0x800548F4` | `sw $s6, 0x14($sp)` | stack | `setupAssetDma` dest, not a second pointer |
| end bound | `0x80054904` | `addu $a0, $s6, $s0` | `$a0` | DMA-size end; not a store |
| converted | `0x80054958`/`0x80054970` | `jal rs_malloc(count*stride+0x14, 0)`; `sw $a0, 0x0($s4)` | slot `+0x0` | different malloc; closed s3634 |
| DMA free | `0x800549E4`/`0x800549E8` | `jal rs_free`; `addu $a0, $s6` | `$s6` | destructor; `blez` count still reaches it; no NULL skip; no post-free NULL |
| epilogue | `0x800549F4` | `lw $s6, 0x50($sp)` | callee-save | restores caller `$s6` |

`$s6` is never stored to a global. `$v0` is `$s5` (slot
index), not `$s6`.

## Object identity

### `$s6` — packed DMA buffer

Sequence:

1. `findTextureByName($a0)` into a halfword. `0xFFFF`
   returns `0xFFFF` before any malloc.
2. `fillTextureDescriptorNoCopy` writes a 0x14-byte
   header at `$sp+0x18`. A zero return, empty pool, or
   no free slot (`+0x6 & 0x8000`) returns `0xFFFF`
   before any malloc.
3. Claim slot `$s4 = 0x80137C84 + index*16` with
   `sh 0x8000, +0x6` and zero `+0x8`/`+0xC`.
4. `get_asset_size_extra($a0=0x80137CFC, $a1=name)` then
   `rs_malloc($v0, 0)` into `$s6`. There is no flags-4
   retry.
5. `get_asset_size_simple` into `$s0` (DMA length).
   `findAssetAcrossSegments` / `setupAssetDma` dest `$s6`
   / `teardownAssetDma`.
6. If DMA length `>= 0x11`, `$s3` walks `$s6` by the
   leading word, 4-byte aligned, counting frames into
   `+0x4($s4)`. `$s3` is reset to `$s6` before convert.
7. `rs_malloc(frameCount * 0x24($sp) + 0x14, 0)` is
   stored at `0x0($s4)`. `zmemcpy` copies the stack
   header into that buffer.
8. Per-frame: `full_header_image_offset_convert($s3+4)`
   relocates interior words *into* `$s6`;
   `loadAndDecodeTexture` copies pixels from `$s3+4`
   into the converted buffer. Neither callee
   `jal rs_free` of `$s6`.
9. `rs_free($s6)`. Return `$s5 & 0xFFFF`.

`$s3` is only a walk alias of `$s6`. Interior stores at
`$s3+4` die with the buffer. `0x14($sp)` is the DMA dest
argument; it is not re-loaded. `setupAssetDma` holds dest
in a command slot until `teardownAssetDma` completes,
which is before this free (same dest-slot contract as
s3612/s3627/s3633). `blez` frame count skips the convert
loop and still reaches the free. Failed malloc (`$s6==0`)
still reaches `rs_free`, which `beq $s0, $zero` and
returns. Early-outs at `L_800549F0` restore the caller's
`$s6` and never `jal rs_free`. Slot `+0x0` is a different
malloc; its destructor is `freeAnimationPhasePool`
(closed s3634).

`loadAndDecodeTexture` `rs_malloc`s a decode dest into
the caller's `0x30($sp)` descriptor and does not
`jal rs_free`. That dest is not `$s6` and is not this
`$a0`.

### Caller-side stores of the return (`$s5`), not `$s6`

Twelve generated callers; none receive `$s6`:

| Caller | Return store | Frees `$s6`? |
|---|---|---|
| `load_dat_file_assets` ×9 | `sh $v0` at `0x801399E8` / `+4` / `+8` / `+C`; first site's `sh` is after `0x80033CC4` and is that callee's halfword | no |
| `initWaterSprayParticles` | none; `$v0` is `$a0` of `setPoolEntryPhaseAndMarkActive` | no |
| `mallocCraftSelectionData` | `sh $v0, 0x800CDA44` | no |
| `npcTrainCarUpdate` | `sh $v0, 0xC8($s2)` | no |

Those halfwords are pool indices consumed by
`setPoolEntryPhaseAndMarkActive` (closed s3634 as a
`+0x6` overlay, not a pointer). No caller
`jal rs_free` of `$s6`.

## Pairing

One generated destructor. Both the convert-loop arm and
the `blez` skip reach it. There is no second `jal rs_free`
of this `$s6`. Sequential double-free would require a
caller to hold `$s6`; no caller-side store exists.
Runtime allocator legitimacy and whether every call's
malloc succeeds remain unproven.

## Classification

The only `jal rs_free` site that can receive this pointer
is `0x800549E4`. The only original heap-pointer writer of
`$s6` is the flags-0 malloc at `0x800548A8`. The `$s3`
walk alias, the DMA dest slot, the converted-buffer
malloc at slot `+0x0`, and the caller-side index stores
are not a second pointer source. This selects
`H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected:
one DMA-buffer identity and one allocator store of that
register.

No guard was added. Runtime allocator state remains
unproven.

## Next remaining `jal rs_free`

Remaining in `funcs_11.c`: `attachedMeshOverlayNpcHandler`
`0x80054344` (`$a0` = `0x1C($s0)`, two-iter `+0x4` walk),
then `load_full_header_image` `0x800544D8` (`$s1`), then
`freeListEntryPointers` `0x80054620` (`0x1C($s0)`).
`funcs_11.c` `jal rs_free` of `$s6` / slot `+0x0` /
`0x80137C84` is exhausted.
