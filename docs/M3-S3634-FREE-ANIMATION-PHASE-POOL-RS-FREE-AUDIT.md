# M3 s3634 — freeAnimationPhasePool rs_free of slot +0x0 / 0x80137C84

## Work unit

Static census of `freeAnimationPhasePool` `jal rs_free`
at `0x80054AC8` (`$a0` = `0x0(0x80137C84 + index*16)`,
gated by `lhu +0x6 & 0x8000`) and `0x80054AEC`
(`$a0` = `0x80137C84`). Enumerated every original
load/store of `0x80137C84` (`0x7C84($reg)` with
`lui 0x8013`) and of slot `+0x0` / `+0x6` (including the
matching `rs_malloc` that becomes the pool base, every
later store that can become either `$a0`, and the
`0x8000` flag writer) and every `jal rs_free` that can
receive those pointers. No build or runtime run was
performed.

The discriminator was the single complete original census of
those two `jal rs_free` sites plus every original `lw`/`sw`
of `0x80137C84` and of `0x0(0x80137C84 + index*16)` and
every caller-side store that can become either `$a0`, and
every `jal rs_free` that can receive those pointers:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadAssetAndIterateSubchunks
`$s6`, freeAllHobFiles slot `+0x8`, releaseMeshAsset `$s5`,
load_hmt_and_hob `$s3`/`0x6C`/`0x74`,
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

Original `jal 0x80001C98` in `funcs_11.c`: 7 sites. Two are
this class (`0x80054AC8`, `0x80054AEC`). The other five are
`attachedMeshOverlayNpcHandler` `0x80054344` (`0x1C($s0)`),
`load_full_header_image` `0x800544D8` (`$s1`),
`freeListEntryPointers` `0x80054620` (`0x1C($s0)`),
`loadAssetIntoNewSlot` `0x800549E4` (that function's `$s6`
DMA scratch), and `loadAssetAndIterateSubchunks` `0x8005519C`
(closed s3633). None of those five loads this pool base or
slot `+0x0`.

`allocAnimationPhasePool` is `0x80054A18`..`0x80054A78`.
`freeAnimationPhasePool` is `0x80054A7C`..`0x80054B08`,
frame `-0x20`. Zero `LOOKUP_FUNC(0x80054A18)` /
`LOOKUP_FUNC(0x80054A7C)`. Single `jr $ra` at `0x80054B04`.

Original `0x7C84` (`lui 0x8013`) accesses. The
`funcs_39.c` `lwc1 -0x7C84($at)` hit is a different
address.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| pool malloc | `0x80054A3C`/`0x80054A50` | `jal rs_malloc(count*28, 0)`; `sw $v0, 0x7C84` | `0x80137C84` | only original store of the pool base |
| count | `0x80054A40` | `sw $s0, 0x7C80` | `0x80137C80` | slot count; not a heap pointer |
| flag init | `0x80054A58` | `sh $zero, 0x6($v1)` | slot `+0x6` | count-bounded `+0x10` walk |
| slot free | `0x80054AA8`..`0x80054AC8` | `lw` pool; `lhu +0x6 & 0x8000`; `lw 0x0`; `jal rs_free` | slot `+0x0` | destructor; no NULL skip; no post-free NULL |
| pool free | `0x80054AE8`/`0x80054AEC` | `lw $a0, 0x7C84`; `jal rs_free` | `0x80137C84` | destructor; no NULL skip; no post-free NULL |
| tick | `0x80054668` | `lw $s2, 0x7C84` | pool | `tickWrappingTimerAccumulatorList` consumer; writes `+0x8`, not `+0x0` |
| claim | `0x80054828`/`0x80054888`/`0x80054970` | `lw $a2, 0x7C84`; `sh 0x8000, +0x6`; `sw malloc, +0x0` | slot | only `+0x0` heap-pointer writer |
| mark | `0x80054B38`/`0x80054B94` | `lw` pool; `ori $a2, 0xC000`; `sh +0x6` | slot `+0x6` | flag overlay; does not write `+0x0` |
| phase | `0x80054BCC` | `lw` pool; `sw +0xC` | slot `+0xC` | not a heap pointer |
| frame | `0x80054C20` | `lw` pool; `lw +0x8`; `lh +0x4` | slot | consumer; no free |

## Object identity

### `0x80137C84` — 16-byte slot pool

Sequence:

1. `allocAnimationPhasePool($a0=count)` stores count at
   `0x80137C80` and `rs_malloc((count*7)<<2, 0)`
   (`count*28` bytes) at `0x80137C84`. The walk uses
   `+0x10` stride (16-byte slots); the extra bytes are
   unused tail of the same malloc, not a second pointer.
2. Count-bounded init zeros each slot `+0x6` only. `+0x0`
   is not stored here.
3. `loadAssetIntoNewSlot` scans for a slot with
   `+0x6 & 0x8000 == 0`, claims it with `sh 0x8000`,
   DMA-loads into a scratch `$s6`, mallocs a converted
   buffer, stores that malloc at `+0x0`, then
   `rs_free($s6)` at `0x800549E4` (a different pointer;
   remaining class).
4. `freeAnimationPhasePool` walks `0x80137C80` slots. If
   `+0x6 & 0x8000`, `rs_free(+0x0)`. Then
   `rs_free(0x80137C84)`. Neither word is NULLed.

`blez` count skips the slot walk and still frees the
pool. Failed pool malloc still reaches `rs_free`, which
NULL-skips. That is not a second pointer source.

### Slot `+0x0` — converted texture buffer

The only original store of `0x0(pool + index*16)` is
`loadAssetIntoNewSlot` `0x80054970`: `$a0` is the
matching `rs_malloc(frameCount * stride + 0x14, 0)`.
Failed malloc stores 0; the later slot free then
`rs_free(NULL)`, which NULL-skips.

`tickWrappingTimerAccumulatorList` loads `+0x0` as a
descriptor base and writes `+0x8` (phase accumulator)
and an interior `+0x10` of that descriptor. It does not
`jal rs_free`.

### `+0x6` `0x8000` flag

Three original stores:

| Writer | Value | Effect on this free |
|---|---|---|
| `allocAnimationPhasePool` `0x80054A58` | 0 | skip the slot free |
| `loadAssetIntoNewSlot` `0x80054888` | `0x8000` | claim; `+0x0` is stored later in the same function |
| `setPoolEntryPhaseAndMarkActive` `0x80054B94` | `$a2 \| 0xC000` | overlay; does not write `+0x0` |

`0xC000` includes `0x8000` and `0x4000`. The `0x4000` bit
is the `tickWrappingTimerAccumulatorList` active gate.
Callers of `setPoolEntryPhaseAndMarkActive` pass `$a2=0`
and `$a0` equal to a `loadAssetIntoNewSlot` return
(`load_dat_file_assets`, `initWaterSprayParticles`,
`mallocCraftSelectionData`) or `lhu 0xC8($s2)` from
`transformCraftAnchorsAndApplySubFx`. The only original
pool-index store of object `+0xC8` is `npcTrainCarUpdate`
`0x800E294C` (`sh` of that same return). A failed load
returns `0xFFFF`; `slt` versus count rejects it. The
`randomParticleWithParentNpcHandler` delay-slot
`sh 0x300, 0xC8` is a different object and out of range
(`0x300 >= count`). The flag overlay is not a second
`+0x0` pointer source.

## Pairing

Six generated `allocAnimationPhasePool` callers
(`initMission` / `setupCutsceneLevel` /
`mallocCraftSelectionData` count `0x10`,
`initInteractiveSceneContext` count `0x20`,
`initVwingHudAndSlotState` / `runModelViewerLoop`
count `0x4`). One generated destructor:
`endMissionCleanup` `0x800FBA94`, reached from two
mutually exclusive `mainGameLoop` `LOOKUP_FUNC(0x800FB9E4)`
arms. There is no second `jal rs_free` of the pool base
or of slot `+0x0`. Sequential double-free of the shared
words is blocked by that pairing. Cinematic / menu /
model-viewer alloc without this destructor leaks the
pool; that is not a second pointer source. Runtime
allocator legitimacy and whether every claimed slot's
converted malloc succeeds remain unproven.

## Classification

The only `jal rs_free` sites that can receive these
pointers are `0x80054AC8` (slot `+0x0`) and `0x80054AEC`
(pool base). The only original heap-pointer writer of
`0x80137C84` is `allocAnimationPhasePool` `0x80054A50`.
The only original heap-pointer writer of slot `+0x0` is
`loadAssetIntoNewSlot` `0x80054970`. The `0xC000` flag
overlay, the `+0x8`/`+0xC` phase words, and the tick
consumer are not a second pointer source. This selects
`H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected:
one pool identity and one converted-buffer identity, each
with a single allocator store.

No guard was added. Runtime allocator state remains
unproven.

## Next remaining `jal rs_free`

Remaining in `funcs_11.c`: `loadAssetIntoNewSlot`
`0x800549E4` (`$a0` = `$s6` = matching DMA
`get_asset_size_extra` `rs_malloc`, freed after the
converted buffer is stored at slot `+0x0`). Then
`attachedMeshOverlayNpcHandler` `0x80054344`
(`0x1C($s0)`), `load_full_header_image` `0x800544D8`
(`$s1`), and `freeListEntryPointers` `0x80054620`
(`0x1C($s0)`).
