# M3 s3647 — reinsertNpcIntoSortedFreeList rs_free of 0x4($npc)

## Work unit

Static census of `reinsertNpcIntoSortedFreeList`
`jal rs_free` at `0x8003EC34` (`$a0` =
`0x4($npc)`). Enumerated every original
load/store of NPC `+0x4` that can become this
`$a0` (including the matching
`slotDispatcherInner` interior store, every
opcode-1 `rs_malloc` store, spawn zeros, and
whether any caller holds the buffer) and every
`jal rs_free` that can receive that pointer.
`0x4($other)` loads into the allocated body
were classified as chunk-interior consumers or
as a second free. No build or runtime run was
performed.

The discriminator was the single complete
original census of that `jal rs_free` site plus
every original `lw`/`sw`/`addu` of NPC `+0x4`
that can become this `$a0`, and every
`jal rs_free` that can receive that pointer.
No overlay duplicate of
`reinsertNpcIntoSortedFreeList` / `0x8003EC10`
exists.

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

Closed classes were not repeated: freeNpcSlotArray
`*0x80130BB0`, destroyNpcContextArrays
`*0x80130BC0`/`*0x80130BC4`/`*0x80130BBC`/
`*0x80130BB8`, freeNpcBurstSpawnerTables
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
same writer as this word.

Sibling `freeNpcSlotArray` `*0x80130BB0` at
`0x8003FC0C` is a different destructor of a
different word (`initNpcSlotList`
`rs_malloc(0x4000, 0)`). It is not this class.
`destroyNpcContextArrays` walks `0x80130BC0` /
`0x80130BC4` chunk heads (s3645); those heads
are the 0x204C mallocs, not `0x4($npc)`.

## Census size

Original `jal 0x80001C98` in `funcs_8.c`: 1
site. It is this class (`0x8003EC34`).
`funcs_8.c` `jal rs_free` is exhausted.

`reinsertNpcIntoSortedFreeList` is
`0x8003EC10`..`0x8003ED70`, frame `-0x18`.
One generated `jal 0x8003EC10`
(`destroyNpcSlotByIndex` `0x8003EDF4`).
Zero `LOOKUP_FUNC(0x8003EC10)`. Zero overlay
lookup of `0x8003EC10`. Single `jr $ra` at
`0x8003ED6C`. No `static_*` clone of these
PCs.

The body is: `lhu 0x14($a0)`; if bit `0x4`
is set, `lw $a0, 0x4($a0)` and
`beq $a0, $zero` skip else `jal rs_free`,
then jump to the epilogue (no post-free
NULL, no flag clear). If bit `0x4` is
clear, reconstruct the 0x204C chunk base
as `0x4($npc) - 0x4C - (0x18($npc) << 7
or << 8)`, reinsert that chunk onto
`0x80130BC0` or `0x80130BC4` (bit `0x1`
selects which), then `sw $zero, 0x4($npc)`
and `andi 0xFFFC` of `+0x14`.

`slotDispatcherInner` is `0x8003EA4C`..
`0x8003EC0C`. Five generated
`jal 0x8003EA4C` (the five spawn
functions). Bit `0x4` skips the whole
chunk path. When clear, it claims a slot
from the 0x204C list and
`sw $v0, 0x4($s1)` at `0x8003EB48` with
`$v0 = chunk + (index << 7 or << 8) +
0x4C` — an interior, not the malloc
base.

`destroyNpcSlotByIndex` is the only
generated caller of this destructor. It
sends handler opcode 2 (`jalr 0x0($npc)`
with `$a1 = 2`) and then `jal 0x8003EC10`.
The 0x1A byte is incremented around that
handler call so a re-entrant destroy
only `ori 0x8` of flags and returns.

## Object identity

`0x4($npc)` is word `+0x4` of a 0x3C
context record from the `0x80130BB8` pool
(s3645). Bit `0x4` of `+0x14` selects the
body identity:

### Owned body (bit `0x4` set) — this free

Spawn writes `$a2` into `+0x14` and zeros
`+0x4` before `jal slotDispatcherInner`.
Fourteen generated `spawnNpcOfType` sites
pass `$a2 = 0x4`. Inherited variants write
flags `1`. `spawnNpcWithSubtype` writes
`$a2 = 0x22`. No generated later `ori 0x4`
of NPC `+0x14` exists; the bit is
spawn-time only.

On the owned path `slotDispatcherInner`
does not write `+0x4`. Opcode 1 of the
handler then `rs_malloc(size, 0)` and
stores the result at `0x4($npc)`.
Confirmed matching stores:

| Handler | PC of store | size |
|---|---|---|
| `randomBurstNpcHandlerVariant` | `0x80040488` | opcode-1 malloc |
| `cutsceneActorNpcHandler` | `0x80044790` | opcode-1 malloc |
| `cinematicSplineWalkerNpcHandler` | `0x8005BD54` | opcode-1 malloc |
| `audioCueDispatcherNpcHandler` | `0x8005C998` | `0x120` |
| `multiEventTemplateNpcHandler` | `0x80070114` | `0x2E0` |
| `randomParticleWithParentNpcHandler` | `0x80074DC8` | `0x110` |
| `heavyAttachedAudioEmitterNpcHandler` | `0x8007BC8C` | opcode-1 malloc |
| `npcPowerGeneratorUpdate` | `0x80077B84` | `0x214` |
| `npcWordDevastatorUpdate` | `0x8007EFB4` | opcode-1 malloc |
| `npcVortexUpdate` | `0x80081B34` | `0xA0` |
| `initHudStruct` | `0x800C0110` (`$t0` = entry `$a0` from `0x80($sp)`) | `0xF80` |
| `hangarVehicleDisplayNpcHandler` | `0x800C691C` | opcode-1 malloc |
| `npcDebrisFieldUpdate` | `0x800D52A0` | opcode-1 malloc |

Each `jal 0x80001ACC` uses `$a1 = 0`.
Those are the original heap-pointer
writers of this word on the owned path.
Spawn zeros are not heap-pointer stores.

Opcode 2 of those handlers frees
*interior* words of the body
(`0x38($body)`, `0x230($body)`, nested
`0xF00`/`0x2B44` closed s3622,
`releaseMeshAsset` of `0x0($body)` /
`0x250($body)`). None `jal rs_free` of
`0x4($npc)` itself. This site is the only
destructor of that pointer.

The owned free NULL-skips. It does not
NULL `+0x4` after a live free. The next
spawn of that 0x3C record zeros `+0x4`
before publishing new flags. A dangling
word on a detached record is not a
second pointer source.

### Pooled interior (bit `0x4` clear) — not this free

`slotDispatcherInner` `rs_malloc(0x204C, 0)`
at `0x8003EA94` publishes the chunk at
`0x80130BC0` / `0x80130BC4` (s3645). The
`0x4($npc)` store is `chunk + (index << 7
or << 8) + 0x4C`. This destructor does
not `jal rs_free` that interior; the
clear-bit arm reconstructs the chunk and
NULLs `+0x4`. `destroyNpcContextArrays`
frees the remaining chunk heads.

## Consumers

NPC-shaped `lw 0x4($npc)` sites load the
word as a body base (filter, transform,
mesh, opcode dispatch).
`spawnChildNpcWithTransform` copies the
parent body pointer into `$s2` and does
not free it. Interior `sw 0x4($body)`
stores (mesh-link words, model-viewer
text, HUD sub-objects) are different
identities. None `jal rs_free` of the
loaded NPC `+0x4`.

No generated caller holds a copy of the
owned malloc across this destructor
except the NPC record itself.

## Pairing

`destroyNpcSlotByIndex` is the only
generated caller of this function. Its
own callers are spawn-replace walks,
transient teardown, and handler opcode-2
/ lethal paths; each sends one destroy
per live slot index. Sequential
double-free of an owned `+0x4` is
blocked by the 0x1A re-entry `ori 0x8`
return, the spawn zero of `+0x4` on
reuse, and the slot-table unlink after
reinsert. Menu / cinematic init without
this destructor can leak an owned
malloc; that is not a second pointer
source.

The s3636 overlay `0x1C`/`0x20` writer is
a different `rs_malloc(0x80, 0)` and is
not this word.

## Verdict

H-NextClassComplete. On the bit-`0x4`
arm, `0x4($npc)` is the matching
flags-0 opcode-1 `rs_malloc` of the
handler body; this is the only
`jal rs_free` of that pointer, with a
NULL skip. On the bit-`0x4`-clear arm
this site does not free `+0x4`.
`funcs_8.c` `jal rs_free` is exhausted.
H-NextClassGap is refuted at static
scope. Runtime allocator legitimacy
(including `rs_free` of a NULL malloc
return, and leak of an owned body if
destroy never runs) remains unproven.
No guard was added.
