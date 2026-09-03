# M3 s3631 — releaseMeshAsset rs_free of $s5

## Work unit

Static census of `releaseMeshAsset` `jal rs_free` at
`0x8005794C` (`$a0` = `$s5` = incoming `$a0`). Enumerated
every original load/store of `$s5` / the incoming object
(including the `lhu 0x8($s5)` `0x1000` gate, the `0x8($s5)`
`& 0x10010000` skip, and every caller-side allocator store
that becomes this `$a0`) and every `jal rs_free` that can
receive that pointer. No build or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw` of
`$s5` in `releaseMeshAsset` and every caller-side store that
can become this `$a0`, and every `jal rs_free` that can
receive that pointer:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: load_hmt_and_hob
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

Original `jal 0x80001C98` in `funcs_12.c`: 10 sites. One is
this class (`0x8005794C`). The other nine are
`loadSpriteSheetTextureFrames` `0x80055450` (closed s3627),
`loadAndRelocateAsset` `0x800555C4` (closed s3626),
`freeTxtFile` `0x800558F8`/`0x80055910` (closed s3628),
`freeSubtitleOverlay` `0x800562CC` (closed s3629),
`load_hmt_and_hob` `0x80056798`/`0x80056D60`/`0x80056D6C`
(closed s3630), and `freeAllHobFiles` `0x80059244`. None of
those nine loads `$s5` as this function's incoming instance.

`releaseMeshAsset` is `0x8005779C`..`0x80057974`, frame
`-0x30`. Sixty-three generated callers. Single `jr $ra` at
`0x80057970`.

Original `$s5` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| save | `0x800577A0` | `sw $s5, 0x24($sp)` | callee-saved | not a heap pointer |
| capture | `0x800577A4` | `addu $s5, $a0` | `$s5` | only heap-pointer writer |
| 0x1000 gate | `0x800577C0`/`0x800577C8` | `lhu 0x8($s5)`; `andi 0x1000`; `bne L_80057864` | flags | skip mesh-walk / HOB `+0x3A` decrement |
| source | `0x800577C4` | `lw $v1, 0x0($s5)` | HOB | `+0x3A` refcount; not `$s5` |
| mesh walk | `0x800577F0`..`0x80057860` | four `+0x18` lists; `enqueueMeshForDeferredRelease($s0)` | interiors | `$s0` is a mesh node, not `$s5` |
| type byte | `0x80057864`/`0x80057888` | `lbu 0xB($s5)` | flags | ring payload at `0x8013A498` |
| 0x80 / 0x100 | `0x80057894`/`0x800578B0` | `lhu 0x8($s5)` | flags | decrement `0x801394E2` / `0x801394E4` |
| pool recycle | `0x800578CC`..`0x80057930` | `lhu 0x8 & 0x4`; index `($s5-0x801394E8)/0xB4` | pool | `j L_80057954` skips `rs_free` |
| 0x10010000 skip | `0x80057934`..`0x80057944` | `lw 0x8($s5) & 0x10010000`; `beq 0x10000 L_80057954` | flags | skip `rs_free` |
| destructor | `0x8005794C`/`0x80057950` | `jal rs_free`; `addu $a0, $s5` | `$s5` | no NULL skip; no post-free NULL |
| restore | `0x80057958` | `lw $s5, 0x24($sp)` | callee-saved | not a heap pointer |

`$s5` is never stored to a global inside this function.
There is no original non-`$a0` writer into `$s5` before the
free.

## Object identity

The incoming pointer is a mesh instance: `+0x0` is the HOB
source (its `+0x3A` is the shared refcount), `+0x8` is the
flag halfword/word, `+0xB` is a type byte. Three original
constructors produce this layout.

### walkMeshdef0List (`0x80056EB0`) — 71 generated callers

Name-hash lookup in `0x80139020`. Two allocation arms that
both store the HOB at `+0x0` and increment HOB `+0x3A`:

1. Pool: `initNpcBookkeepingTables` `rs_malloc(0x4380)` at
   `0x801394E8` (96 × `0xB4`). Pop a slot, `sh 4, 0x8`.
   `releaseMeshAsset` recycles the slot and skips `rs_free`.
2. Heap: `rs_malloc` of the expanded node size,
   `sh $zero, 0x8`. Word `+0x8` is 0, so
   `(word & 0x10010000) != 0x10000` and `rs_free` runs.

### instantiateNamedMeshInstance (`0x80057338`) — 5 generated callers

Always `rs_malloc(*(src-4)+0x58)`, `sh 0x1001, 0x8`. On
big-endian that word is `0x10010000`, which is not
`0x10000`, so `rs_free` runs. The `0x1000` bit skips the
mesh-walk. Stores: `orientedNpcHandler` `0x0($s2)`,
`npcWaterSprayUpdate` `0x30($s1)`, `npcWakeUpdate`
`0x78`/`0x7C($s5)`, `spawnCutsceneObjectsFromList`
`+0x50`/`+0x54`.

### createMeshInstanceFromSource (`0x80059294`) — 2 generated callers

`rs_malloc(0xB4, 0)` when `$a1==0`, else the provided
buffer. `sh 1, 0x8` → word `0x00010000` → skip `rs_free`.
`loadEffectModelInstancePool` passes
`rs_malloc(0x3A20)+i*0xF8+0x40` (`0x3C` slots).
`freeEffectModelInstancePool` calls `releaseMeshAsset` with
the matching `+0x40` delay-slot add, then `rs_free`s the
outer `0x3A20`. That outer free is a different pointer.

## Pairing

Sixty-three `jal 0x8005779C` sites. `$a0` is always a
constructor return:

| Slot | Constructor store | Destructor |
|---|---|---|
| NPC `0x30` | `walkMeshdef0List` / `instantiateNamedMeshInstance` | opcode-2 `releaseMeshAsset` |
| player `0x0` | `walkMeshdef0List` `0x0($s1)` | opcode-2 |
| player AT-ST `0x0($s4)` | `walkMeshdef0List` `0x7DBC($s0)` with `$s4=$s0+0x7DBC` | opcode-2 |
| DAT `0x0($s0)` | `walkMeshdef0List` via `$v1=$v0` | `parseDatItemSubtypes1To5` |
| spline `0xED4` / `0x18` | `walkMeshdef0List` | opcode-2 walk then `0x18` |
| wake `0x78`/`0x7C` | `instantiateNamedMeshInstance` | opcode-2 |
| missile `0x2C` | `walkMeshdef0List` | opcode-2 |
| HUD `0x250` | `walkMeshdef0List` | `initHudStruct` teardown |
| preview `0x10` | `walkMeshdef0List` | `setupCraftPreviewModel` |
| viewer `0x34(0x800D00B0)` | `loadModelViewerModels` stride-`0x30` slot `+0x4` | `runModelViewerLoop` then NULL |
| viewer tables | `loadModelViewerModels` `+0x4` / `+0x0` | `releaseModelViewerModelAssets` NULL-skips the first table |
| effect pool `+0x40` | `createMeshInstanceFromSource` into `0x3A20` interiors | skip-`rs_free` then outer free |
| temps | `walkMeshdef0List` `$v0` never stored | `loadDatFile` / `loadSfxAsset` / `initWaterSprayParticles` (`$s6` delay-slot save of `$v0`) |

`freeJfifDecodeState` `lw $a0, 0x30($s2)` is a JPEG buffer,
not this instance. No other generated `jal 0x80001C98`
receives a walkMeshdef0List / instantiateNamedMeshInstance /
createMeshInstanceFromSource return.

Opcode-2 paths run once per live slot. Temps are one
stack frame. Viewer `0x34` is NULLed after its free.
Failed mallocs return NULL; `rs_free` itself
`beq $s0, $zero`. Pool double-recycle and heap
allocator legitimacy remain unproven.

## Classification

The only `jal rs_free` that can receive these instance
pointers is `0x8005794C`. `$s5` is the incoming `$a0`.
Every caller-side store is one of the three constructors.
The `0x1000` gate skips the mesh-walk only. The `0x4` bit
recycles a pool slot and does not `rs_free`. The
`0x10010000 == 0x10000` skip is the `sh 1, 0x8` create
path, whose storage is either skipped or the interior of
the `0x3A20` malloc. No original non-allocator writer
exists. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: one object
layout, three matching constructors, one destructor.

No guard was added. Runtime allocator state, pool
freelist reuse, and pairing of kept HOBs with
`freeAllHobFiles` remain unproven.
