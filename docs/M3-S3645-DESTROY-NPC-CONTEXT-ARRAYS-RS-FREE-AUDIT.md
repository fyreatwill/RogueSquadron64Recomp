# M3 s3645 — destroyNpcContextArrays rs_free of *0x80130BC0 / *0x80130BC4 / *0x80130BBC / *0x80130BB8

## Work unit

Static census of `destroyNpcContextArrays` `jal rs_free`
at `0x8003FE28` (`$a0` = `*0x80130BC0`), `0x8003FE50`
(`$a0` = `*0x80130BC4`), `0x8003FE6C` (`$a0` =
`*0x80130BBC`), and `0x8003FE78` (`$a0` =
`*0x80130BB8`). Enumerated every original load/store of
those four words (including the matching malloc stores,
the linked-list `0x48($a0)` walk that republishes
`0xBC0`/`0xBC4`, every later store that can become these
`$a0`s, and whether any caller holds the buffers) and
every `jal rs_free` that can receive those pointers. No
build or runtime run was performed.

The discriminator was the single complete original
census of those `jal rs_free` sites plus every original
`lw`/`sw`/`addu` of `0x80130BC0` / `0x80130BC4` /
`0x80130BBC` / `0x80130BB8` and every caller-side store
that can become these `$a0`s, and every `jal rs_free`
that can receive those pointers. No overlay duplicate of
`destroyNpcContextArrays` / `0x8003FDD8` exists.

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

Closed classes were not repeated: freeNpcBurstSpawnerTables
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
same writer as one of these four words.

Sibling `freeNpcSlotArray` `*0x80130BB0` at
`0x8003FC0C` is a different destructor of a
different word (`initNpcSlotList`
`rs_malloc(0x4000, 0)`). It is not this class.

## Census size

Original `jal 0x80001C98` in `funcs_9.c`: 14 sites.
Four are this class (`0x8003FE28` / `0x8003FE50` /
`0x8003FE6C` / `0x8003FE78`). One is
`freeNpcSlotArray` (left as the following unit).
Three are `freeNpcBurstSpawnerTables` (closed
s3644). One is `computeGridTileEdgeAdjacencyMasks`
(closed s3643). Five are
`teardownAnimatedMapGridLayer` (closed s3642).
None of those other ten loads these four words.

`destroyNpcContextArrays` is `0x8003FDD8`..
`0x8003FE98`, frame `-0x20`. One generated
`jal 0x8003FDD8` (`endMissionCleanup`
`0x800FBA74`). Zero `LOOKUP_FUNC(0x8003FDD8)`.
Single `jr $ra` at `0x8003FE94`.

The body is: while `*0x80130BC8 < 0xBF` call
`destroyTransientNpcSlots` (walks `*0x80130BB0`,
does not load these four words); NULL-skip walk
of `*0x80130BC0` following `0x48($a0)` and
`rs_free` each node; the same walk of
`*0x80130BC4`; then `rs_free(*0x80130BBC)` and
`rs_free(*0x80130BB8)` with no NULL skip; then
NULL `0xBBC` and `0xBB8`. The `0x48` republish
is the jal delay-slot `sw` of the next pointer
into the head, before the free. After the last
node, the head is that node's `0x48`, which
generated init writes as 0. No explicit post-walk
NULL of `0xBC0`/`0xBC4`.

`allocNpcContextArrays` is `0x8003FD54`..
`0x8003FDD4`, frame `-0x18`. Three generated
`jal 0x8003FD54`. Zero `LOOKUP_FUNC(0x8003FD54)`.
Single `jr $ra` at `0x8003FDD0`. Both pointer
stores and the two zero-inits of `0xBC0`/`0xBC4`
execute on every entry.

No absolute `0x80130BC0` / `0x80130BC4` /
`0x80130BBC` / `0x80130BB8` encodings exist
outside `lui 0x8013` plus `0xBC0` / `0xBC4` /
`0xBBC` / `0xBB8`. No `-0xF440` / `-0xF43C` /
`-0xF444` / `-0xF448` aliases from
`0x80140000`. Coincidental `addiu ..., 0xBC0`
sites are `lui 0x8011` (`0x80110BC0`) or
`lui 0x800B` (`0x800B0BC0`).
`lb -0xBBC($zero)` is float-as-code, not this
word.

`funcs_8.c` has one `jal rs_free`
(`0x8003EC34`): `$a0` is `0x4($npc)` on the
bit-`0x4` skip of `reinsertNpcIntoSortedFreeList`,
not any of these four words.

## Object identity

### `0x80130BB8` — 192-slot context pool, stride 0x3C

`rs_malloc(0x2D00, 0)` at `0x8003FD64`. Delay-slot
`sw $v0, 0xBB8($s0)` at `0x8003FD7C` (`$s0` =
`lui 0x8013`). `0x2D00 / 0x3C = 0xC0`. Only
original heap-pointer store of the word.

The only other original load is the fill
`lw $a0, 0xBB8($s0)` at `0x8003FD88`, which
computes `BB8+0x2CC4` (`0x3C * 0xBF`) as the
last-slot address for the `0xBBC` table. The
destructor load at `0x8003FE74` is the free.
Post-free `sw $zero, 0xBB8($s0)` at
`0x8003FE8C`. No consumer loads `0xBB8` as a
call-held copy.

### `0x80130BBC` — pointer table into the 0xBB8 pool

`rs_malloc(0x300, 0)` at `0x8003FD78`.
`sw $v0, 0xBBC($v1)` at `0x8003FD90`.
`0x300 / 4 = 0xC0` entries. Only original
heap-pointer store of the word.

A 0xC0-iter walk then writes descending
`BB8 + i*0x3C` addresses into the table
(start `v0+0x2FC`, `sw $a0, 0x0($a1)`,
`$a1 -= 4`, `$a0 -= 0x3C`). Those entries
are interiors of the `0xBB8` buffer, not
separately allocated.

Five spawn consumers load the word as a table
base indexed by `*0x80130BC8 << 2` and pop
one 0x3C record (`spawnInheritedNpcVariantA/B/C`,
`spawnNpcWithSubtype`, `spawnNpcOfType`). They
zero `+0x4`/`+0x8` of that record and later
`jal slotDispatcherInner`. None `jal rs_free`.
`destroyNpcSlotByIndex` writes a returned
record back through `0xBBC[BC8++]` at
`0x8003EEDC`; that stores an interior of
`0xBB8`, not a second heap pointer into
`0xBBC` itself.

The destructor load at `0x8003FE68` is the
free. Post-free `sw $zero, 0xBBC($s1)` at
`0x8003FE84`.

### `0x80130BC0` / `0x80130BC4` — sorted 0x204C chunk lists

`allocNpcContextArrays` stores 0 to both
(`0x8003FDCC` / `0x8003FDC4`). Those are not
heap-pointer stores.

The only `rs_malloc` of a value that can become
these heads is `slotDispatcherInner`
`rs_malloc(0x204C, 0)` at `0x8003EA94` when
`*head == 0`. Bit `0x1` of NPC `+0x14` selects
`$s0 = &0x80130BC0`, else `&0x80130BC4`. Bit
`0x4` skips the whole chunk path. New chunks
zero `+0x44`/`+0x48` and fill 64 slot-index
bytes. `sw $a0, 0x0($s0)` at `0x8003EADC`
publishes the malloc as the head.

Later stores of these two words are list
relinks of that same malloc identity:

- Exhausted-chunk unlink (`lb 0x0($chunk) < 0`
  and `+0x44 == 0`): `sw 0x48($chunk), 0x0($s0)`
  at `0x8003EB74`. Then `+0x48` of the unlinked
  chunk is zeroed. The chunk is off the list
  until reinsert.
- Sorted reinsert of a live chunk:
  `sw $a0, 0x0($s0)` at `0x8003EBE0` when the
  previous `+0x44` is 0.
- `reinsertNpcIntoSortedFreeList` reconstructs
  the chunk base as `0x4($npc) - 0x4C -
  (index << 7 or << 8)` — the matching interior
  inverse of `slotDispatcherInner`'s
  `sw $v0, 0x4($s1)` — and may
  `sw $a1, 0x0($a3)` at `0x8003ECEC` /
  `0x8003ED1C` (`$a3` is `&0xBC0` or `&0xBC4`).
  `0x4($npc)` is not one of these four words.

The destructor walks `0x48($a0)` and
`rs_free`s each remaining head. `0x48` writers
are those same chunk mallocs or 0. No generated
store publishes a non-allocator pointer into
either head.

Consumers load the heads only inside
`slotDispatcherInner` / `reinsertNpcIntoSortedFreeList`
as list bases. None `jal rs_free` of the head
except this destructor.

Unlinked exhausted chunks are not on the
destructor walk. `destroyTransientNpcSlots`
runs first and `jal destroyNpcSlotByIndex` →
`reinsertNpcIntoSortedFreeList`, which can put
those chunks back. A live non-transient NPC
holding an interior `+0x4` can leave its chunk
unlinked across teardown; that is a leak of a
matching malloc, not a second pointer source.

## Pairing

`allocNpcContextArrays` has three generated
callers:

| Caller | PC |
|---|---|
| `initMission` | `0x800FA294` |
| `initSceneForMission` | `0x800A9C9C` |
| `initInteractiveSceneContext` | `0x800C415C` |

It always overwrites `0xBB8`/`0xBBC` with fresh
allocator returns, zeros `0xBC0`/`0xBC4` without
freeing any live list, and does not free the
previous `0xBB8`/`0xBBC`. Menu
`initInteractiveSceneContext` without this
destructor leaks the first mallocs; that is not
a second pointer source. A second alloc while
lists are live also leaks unlinked `0x204C`
chunks.

`endMissionCleanup` has two generated callers,
both in `mainGameLoop`: `0x8003E2C4` and
`0x8003E388` (`LOOKUP_FUNC(0x800FB9E4)`). Those
arms are mutually exclusive (s3624). Sequential
double-free of `0xBBC`/`0xBB8` is blocked by
that pairing plus the post-free NULLs.
`0xBC0`/`0xBC4` skip on NULL.

The s3636 overlay `0x1C`/`0x20` writer is a
different `rs_malloc(0x80, 0)` and is not one
of these four words.

## Verdict

H-NextClassComplete. Matching flags-0
`rs_malloc(0x2D00, 0)` of `0x80130BB8`,
`rs_malloc(0x300, 0)` of `0x80130BBC`, and
`rs_malloc(0x204C, 0)` list heads at
`0x80130BC0`/`0x80130BC4` (plus 0 from init
and `0x48` relinks of those same mallocs). One
destructor; spawn consumers load `0xBBC` as a
table base and do not `jal rs_free`. No second
live `jal rs_free` of those pointers.
H-NextClassGap is refuted at static scope.
Runtime allocator legitimacy (including
`rs_free` of a NULL malloc return, and leak of
unlinked exhausted chunks) remains unproven.
No guard was added.
