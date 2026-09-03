# M3 s3641 — teardownGridLayerWorker rs_free of *0x80137614

## Work unit

Static census of `teardownGridLayerWorker` `jal rs_free` at
`0x800495C0` (`$a0` = `*0x80137614`). Enumerated every
original load/store of that word (including the matching
`rs_malloc` in `loadLevelTextureCache` at `0x80048180`,
every later store that can become this `$a0`, and whether
any caller holds the buffer) and every `jal rs_free` that
can receive that pointer. No build or runtime run was
performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of `0x80137614` and every caller-side store that can become
this `$a0`, and every `jal rs_free` that can receive that
pointer:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeGridCellBuffers
`*0x80137A5C`/`*0x80137A54`/`*0x80137A4C`/`*0x80137A68`,
loadLevelTextureCache `$s0` 0x136C scratch,
freeLevelDatBuffers `*0x801375D0`/`*0x801375D8`/
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
identifies that same writer as this word.

## Census size

Original `jal 0x80001C98` in `funcs_10.c`: 9 sites. One is
this class (`0x800495C0`). Four are `freeGridCellBuffers`
(closed s3640). Three are `freeLevelDatBuffers` (closed
s3638). One is `loadLevelTextureCache` `$s0` (closed
s3639). None of those eight loads this word.

`teardownGridLayerWorker` is `0x800495B0`..`0x800495F8`,
frame `-0x18`. One generated `jal 0x800495B0`
(`teardownAnimatedMapGridLayer` `0x80045768`). Zero
`LOOKUP_FUNC(0x800495B0)`; zero `lui`/`addiu`
function-pointer constructions of `0x800495B0`. Single
`jr $ra` at `0x800495F4`. The body is straight-line: load
`*0x80137614` into `$a0`, `jal rs_free`, then
`unregisterServiceWorker(*0x80137A40)` and
`teardownAssetDma(*0x80138920, *0x80137A48)`. No original
branch skips the free. No NULL skip and no post-free NULL
of `0x80137614`.

`loadLevelTextureCache` is `0x80048104`..`0x80048430`,
frame `-0x38`. Two generated `jal 0x80048104`; zero
`LOOKUP_FUNC(0x80048104)`; the only `0x8104` immediate is
`lui $zero, 0x8104` in `funcs_27.c`, which does not build
this address. Single `jr $ra` at `0x8004842C`. The
`rs_malloc` at `0x80048164` uses flags-0 (`$a1 = 0`). The
store at `0x80048180` is the delay slot of
`beq $v0, $zero, L_800481B8` and also the fallthrough, so
it executes on every entry.

Generated `0x7614` immediates: 21 in `funcs_10.c` (one
`sw`, twenty `lw`) and one coincidental
`lwc1 $f28, -0x7614($at)` in `funcs_41.c` with
`$at = lui 0x800B` (rodata float at `0x800A89EC`), not
this word. No `addiu` of `0x7614`. Every `lw`/`sw` of
`0x7614($reg)` uses a `lui 0x8013` base (`$v0`/`$v1`/
`$a0`/`$s3`/`$t0`). `$s3` is callee-saved and loaded
at `0x80048310` before `registerHmtTextureInTable`. `$t0`
in `processGridCellByDistance` is reloaded by `lui 0x8013`
at `0x800490CC` / `0x80049190` / `0x800491A4` with no
`jal` before the later `0x7614($t0)` loads.

## Object identity

### `0x80137614` — count-table malloc, stride 12

Sequence in `loadLevelTextureCache`:

1. Incoming `$s0` is a reserved-size constant (`0x1000`
   from `initMission`, `0x5DC0` from `load_cutscene`).
   `getLoadedTextureCount` minus that reserved size is
   converted (magic `0x3E0F83E1`, `srl 9`) into an
   extra-slot count plus 4, stored at `0x80137A44`.
   `lui $s0, 0x8013` then overwrites the reserved-size
   value. That incoming `$a0` is not this pointer
   (closed s3639).
2. Size = `count * 12` (`$v0<<1 + $v0 << 2`).
3. `rs_malloc(count*12, 0)` at `0x80048164`.
4. Delay-slot `sw $a0, 0x7614($v1)` at `0x80048180`
   (`$a0` = `$v0`, `$v1` = `lui 0x8013`). This is the
   only original store of the word.

When `count > 5`, a walk from index 5 writes neighbor
index halfwords at `base + i*12 + 0x0/+0x2`. Both arms
then load the word as a table base and write header
halfwords: `+0x3C = 3`, last-entry `-0xA = 4`, first
three slots `+0x0/+0x2 = 0xFFFF` (stride 0xC),
`+0x24 = 0xFFFF`, `+0x26 = 5`, `+0x30 = count-1`,
`+0x32 = 0xFFFF`. When `count > 5`, the register loop
writes texture-id halfwords at `base + 0x3C + i*0xC`
(`+0x4`, `+0x6`) and `0xFFFF` at `+0x8`. Those stores
are into the buffer, not a second heap pointer.

The later `rs_malloc(0x136C, 0)` rebound into `$s0` at
`0x80048248` is a different scratch buffer, freed inside
the same function at `0x80048378` (closed s3639). The
s620 host jump at that rebind does not skip the
`0x80137614` store.

### Consumers — table-base loads, no `jal rs_free`

| Function | PCs | Use |
|---|---|---|
| `loadLevelTextureCache` | `0x800481C0`, `0x80048220`, `0x80048340`, `0x80048358` | header / register-loop halfword stores |
| `buildGridCellAdjacencyTable` | `0x8004844C`, `0x8004848C`, `0x800484E0` | table-base halfword fill; no `jal` |
| `processGridCellByDistance` | `0x80049074`, `0x800490DC`, `0x80049118`, `0x80049160`, `0x800491A8`, `0x80049218`, `0x80049280` | `index*12` slot, halfword unlink/relink; the only `jal` is `0x80006F78` after the last load |
| `recycleGridCellToFreeList` | `0x80049444`, `0x800494E4`, `0x80049500`, `0x8004954C` | table-base halfword recycle; `jr $ra` with delay-slot `sh 0xFFFF, 0x2(base)` |

None of those loads is `$a0` of a `jal rs_free`.

### Sibling words in the same loader — different identities

After the `$s0` scratch free, `loadLevelTextureCache`
registers a service worker at `0x80137A40` and an asset
DMA handle at `0x80137A48`. `teardownGridLayerWorker`
unregisters those after this free; they are not this
pointer. `addiu $a0, $v1, 0x7620` is BSS `0x80137620`
(32-iter byte fill, stride 0x20), not the malloc.
`0x80137A20` is a separate 32-iter zero-fill. Count
word `0x80137A44` is an integer.

### Incoming `$a0` of `loadLevelTextureCache` — reserved size, discarded

| Caller | PC | `$a0` | Skip |
|---|---|---|---|
| `initMission` | `0x800FA67C` | `0x1000` | `*0x80130B70 == 0xA` |
| `load_cutscene` | `0x800A688C` | `0x5DC0` | `$s0 == 0xA` (`lbu 0x30($sp)`) |

Neither caller holds a buffer across the call. A second
`loadLevelTextureCache` mallocs a new table, stores it
at `0x80137614`, and leaks the previous publish. That is
not a second pointer source for this free.

## Pairing

`initMission` / `load_cutscene` skip `loadLevelTextureCache`
when the type is `0xA`. `teardownAnimatedMapGridLayer`
skips `teardownGridLayerWorker` (and `freeGridCellBuffers`
plus the sibling `0x6FCC` / `0x6E1C` frees) on
`*0x80130B70 == 0xA`. Paired skip: type `0xA` never
publishes this word and never frees it. A type change
between load and teardown can leak or `rs_free` BSS-zero;
`rs_free` itself `beq $s0, $zero` and returns. That is
not a second pointer source.

One generated destructor (`teardownGridLayerWorker`),
reached from `teardownAnimatedMapGridLayer`:

| Wrapper | PC | Route |
|---|---|---|
| `endMissionCleanup` | `0x800FBAB4` | `mainGameLoop` `0x8003E2C4` and `0x8003E388` via `LOOKUP_FUNC(0x800FB9E4)` |
| `cinematicShutdownAudioAndAssets` | `0x800AF270` | `cinematicLoopBody` `0x800A64EC` |

Those two wrappers are the matching destructors of the
two `loadLevelTextureCache` callers (mission vs cinematic).
The two `mainGameLoop` arms are mutually exclusive
(same pairing as s3624 / s3629 / s3638 / s3640).
Sequential double-free of this word is blocked by that
caller pairing; the destructor does not NULL after
release.

Zero `LOOKUP_FUNC` of `0x80048104`, `0x800495B0`, or
`0x80045708`. Failed malloc (`$v0 == 0`) still stores 0
and reaches `rs_free`, which skips. The header and
register-loop stores would dereference the pointer first.
That is the same unproven allocator-failure edge
s3604–s3640 left open.

This word is not the s3636 overlay `0x1C`/`0x20` writer.

## Classification

The only `jal rs_free` site that can receive this pointer
is `0x800495C0`. The only original heap-pointer writer of
`0x80137614` is the flags-0 `rs_malloc(count*12, 0)` store
at `0x80048180`. Interior table halfwords, the `0x136C`
scratch `$s0`, the worker/DMA handles, BSS `0x80137620`,
count word `0x80137A44`, and all consumer table-base
loads are not a second pointer source. This selects
`H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected:
one pointer identity and one allocator store.

No guard was added. Runtime allocator state remains
unproven. The s3636 overlay skip-path NULL store was not
landed: this word is not that writer.

## Next remaining `jal rs_free`

`funcs_10.c` `jal rs_free` is exhausted. The next
remaining original sites are in `funcs_9.c`:
`teardownAnimatedMapGridLayer` `0x80045730`
(`*0x80136DC8`), `0x8004573C` (`*0x80136DCC`),
`0x80045748` (`*0x80136FC4`, NULLed after),
`0x80045780` (`*0x80136FCC`), and `0x80045790`
(`*0x80136E1C`, the `loadLevelAssets` `n*24` sibling
from s3640).
