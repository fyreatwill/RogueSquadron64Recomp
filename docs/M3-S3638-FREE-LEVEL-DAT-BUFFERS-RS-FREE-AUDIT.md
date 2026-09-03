# M3 s3638 — freeLevelDatBuffers rs_free of *0x801375D0 / *0x801375D8 / *0x801375F4

## Work unit

Static census of `freeLevelDatBuffers` `jal rs_free` at
`0x80047B0C` (`$a0` = `*0x801375D0`), plus the sibling
frees of `*0x801375D8` at `0x80047B20` (delay-slot
`sw $zero, 0x801375D0`) and `0x1C($s0)` at
`0x80047B2C` (`$s0` = `0x801375D8`, so `0x801375F4`).
Enumerated every original load/store of those three words
(including the matching `rs_malloc` / `load_asset`, every
later store that can become these `$a0`s, and whether any
caller holds the buffers) and every `jal rs_free` that can
receive those pointers. No build or runtime run was
performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original `lw`/`sw`/`addu`
of `0x801375D0` / `0x801375D8` / `0x801375F4` and every
caller-side store that can become these `$a0`s, and every
`jal rs_free` that can receive those pointers:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: load_full_header_image `$s1`,
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
mix-table, pan-input, or hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_10.c`: 10 sites. Three
are this class (`0x80047B0C` / `0x80047B20` / `0x80047B2C`).
The other seven are `loadLevelTextureCache` `0x80048378`
(`$s0` rebound to a later `rs_malloc(0x136C, 0)`),
`freeGridCellBuffers` `0x8004956C`/`0x8004957C`/
`0x8004958C`/`0x8004959C` (`0x80137A5C` / `0x80137A54` /
`0x80137A4C` / `0x80137A68`), and
`teardownGridLayerWorker` `0x800495C0` (`0x80137614`).
None of those seven loads these three DAT words.

`freeLevelDatBuffers` is `0x80047AF8`..`0x80047B44`,
frame `-0x20`. One generated `jal 0x80047AF8`
(`endMissionCleanup` `0x800FBAAC`). Zero
`LOOKUP_FUNC(0x80047AF8)`; zero `lui`/`addiu`
function-pointer constructions of `0x80047AF8`. Single
`jr $ra` at `0x80047B40`. The body is straight-line: no
original branch skips any of the three frees.

Original accesses of the three words:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| DAT publish | `0x80046DBC` | `sw $s2, 0x75D8($v0)` | `0x801375D8` | only original heap-pointer writer of D8; `$s2` = `load_asset` `$v0` |
| dim W | `0x80046F10`/`0x80046F18` | `sw $v0, 0x14($v1)` | `0x801375EC` | grid width; not a heap pointer |
| dim H | `0x80046F34`/`0x80046F3C` | `sw $v0, 0x18($v1)` | `0x801375F0` | grid height; not a heap pointer |
| grid malloc | `0x8004702C`/`0x8004704C` | `jal rs_malloc(($14*$18)<<1, 0)`; `sw $v0, 0x1C($s0)` | `0x801375F4` | only original heap-pointer writer of F4; `$s0` = `0x801375D8` |
| count zero | `0x80047098` | `sw $zero, 0x75D4` | `0x801375D4` | spawn-pointer count; not a heap pointer |
| D0 malloc | `0x80047144`/`0x80047160` | `jal rs_malloc(count<<2, 0)`; `sw $v0, 0x75D0($s0)` | `0x801375D0` | only original heap-pointer writer of D0; flags-0 |
| D0 empty | `0x800471E0` | `sw $zero, 0x75D0($v0)` | `0x801375D0` | count==0 skip; NULL, not a second pointer |
| D0 fill | `0x800471AC` | `lw 0x75D0`; `sw` into `$a0` | D0 buffer | stores DAT item pointers *into* the malloc |
| D0 consumers | `0x80047714`/`0x8004773C`/`0x80047750` | `lw 0x75D0` | D0 buffer | `updateActiveGridCellState` table walk; no `jal rs_free` |
| free D0 | `0x80047B04`/`0x80047B0C` | `lw $a0, 0x75D0`; `jal rs_free` | `0x801375D0` | destructor; no NULL skip |
| free D8 | `0x80047B18`/`0x80047B20` | `lw $a0, 0x75D8`; `jal rs_free` | `0x801375D8` | destructor; delay-slot NULLs D0 |
| free F4 | `0x80047B28`/`0x80047B2C` | `lw $a0, 0x1C($s0)`; `jal rs_free` | `0x801375F4` | destructor; no post-free NULL of D8 or F4 |

`$s2` in `loadDatFile` is assigned once from `load_asset`
`$v0` at `0x800467F0` and restored only in the epilogue.
`loadDatFile` has no `jal rs_free` and one `jr $ra`.

## Object identity

The three words are sibling fields of one global DAT
context at `0x801375D8` (`+0x0` file pointer, `+0x4`..`+0x10`
bounds floats, `+0x14`/`+0x18` dimensions, `+0x1C` grid).
They are three different allocations.

### `0x801375D8` — loaded DAT file

Sequence:

1. `sprintf` of the incoming name, then `load_asset`.
   `load_asset` `jal rs_malloc` at `0x800648C0` and rebinds
   `$s2` to `$v0` at `0x800648DC` (same contract as s3614).
2. Interior offset-to-pointer walks mutate words *inside*
   that buffer (`0x4($s2)`, `0x1C($s2)`, `0x14($s2)`,
   `0x34($s2)`, …). Those stores die with the buffer. The
   `0x1C($s2)` convert (`$s2 + file_offset`) is not the
   global `0x801375F4`.
3. `lbu 0x80130B3A`. If that byte equals 1, `j L_80047334`
   with delay-slot `addu $v0, $s2` — skip every publish
   store and return `$s2`. If it is not 1, `sw $s2,
   0x801375D8` at `0x80046DBC` and continue.
4. On the publish path the later epilogue edges set
   `$v0 = 0`. So `$v0` is `$s2` xor the D8 store.

s3614 inverted this polarity (it described the return-`$s2`
edge as `0x80130B3A != 1`). The generated branch is
`bne $v1, 1, L_80046DA8` then store; fall-through is the
skip/return. The exclusivity still holds: D8 and a
caller-side `$v0` store cannot both hold this `$s2`.

`menuOverlayInit` `0x800C5904` is the only original
`sb 1, 0x80130B3A`. Two original zeros
(`0x800C5D90`, `0x8006DA90`) restore it.

### `0x801375F4` — grid halfword table

On the same publish path, `$s0 = 0x801375D8`,
`rs_malloc((0x14($s0)*0x18($s0))<<1, 0)`, then
`sw $v0, 0x1C($s0)` even when the product is `blez`
(delay slot). A fill loop writes `0xFFFF` halfwords into
that buffer. `parseDatItemCommon` and
`updateActiveGridCellState` load `0x1C` of the global
address as a table base and do not `jal rs_free`.

The skip path never reaches this malloc, so F4 is left as
BSS-zero or a previous publish's pointer.

### `0x801375D0` — spawn-item pointer table

Still on the publish path: count at `0x801375D4` is zeroed,
then incremented for selected items. If the count is 0,
`sw $zero, 0x801375D0` and skip the malloc. Otherwise
`rs_malloc(count<<2, 0)` and `sw $v0, 0x801375D0`. The
fill loop writes DAT item pointers into that buffer.
`updateActiveGridCellState` loads D0 as a table base and
does not free it.

### Skip-path `$v0` stores are not a second D8/F4/D0 source

Four generated `jal 0x80046784`; zero
`LOOKUP_FUNC(0x80046784)`:

| Caller | PC | `$v0` store | Frees D8/F4/D0? |
|---|---|---|---|
| `loadLevelAssets` | `0x8004546C` | none (next `sprintf`) | no |
| `initCraftSelectScreen` | `0x800AEFB0` | `0x800CDCE8`; later `getDatItemByName` | no |
| `initModelViewer` | `0x800CA6F4` | `0x800D03CC`; `shutdownModelViewer` `rs_free` (s3614) | no: that free is of the skip-path return, which is exactly the path that does not store D8 |
| `mallocCraftSelectionData` | `0x800A9668` | `0x800CC58C`; later `findDatItemInTableByName` | no |

`load_dat_file_assets` loads D8 as a walk base and has no
`jal rs_free`. `preloadSceneReferencedSongs` loads D8
`+0x30`/`+0x34` and frees its own scratch `$s2`/`$s3`,
not these words. `getLevelDatItemByName` loads D8 and
forwards it to `getDatItemByName`. Every other generated
`0x75D8` load is a DAT-base consumer with no `jal rs_free`
of that pointer.

A B3A==1 `loadLevelAssets` call leaks `$s2` (return
discarded, D8 not stored). A second `loadDatFile` without
`freeLevelDatBuffers` overwrites D8/F4/D0 and leaks the
previous publish. Neither is a second pointer source for
these three frees.

## Pairing

One generated destructor, reached from two mutually
exclusive `mainGameLoop` arms (`0x8003E2C4` and
`0x8003E388` via `endMissionCleanup`). The straight-line
body always reaches all three `jal rs_free`. `rs_free`
itself `beq $s0, $zero` and returns, so a BSS-zero or
count-0 D0 is a skip, not a Gap.

D0 is NULLed in the delay slot of the D8 free. D8 and F4
are not NULLed. Sequential double-free of those two words
is blocked by the single generated destructor and the
mutually exclusive teardown arms (same pairing as s3624 /
s3629). Runtime allocator legitimacy and whether every
call's malloc succeeds remain unproven.

Failed malloc (`$s2`/`F4`/`D0` == 0) still reaches
`rs_free`, which skips. The interior convert walk would
dereference `$s2` first. That is the same unproven
allocator-failure edge s3604–s3637 left open.

## Classification

The only `jal rs_free` sites that can receive these
pointers are `0x80047B0C` / `0x80047B20` / `0x80047B2C`.
The only original heap-pointer writers are the publish-path
`load_asset` store of D8, the flags-0 grid malloc of F4,
and the flags-0 count-sized malloc of D0 (or the matching
NULL when count is 0). Interior DAT-buffer converts, the
skip-path `$v0` return, and D8 consumers are not a second
pointer source. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: three pointer
identities and one allocator store each.

No guard was added. Runtime allocator state remains
unproven. The s3636 overlay skip-path NULL store was not
landed: these words are not that writer.

## Next remaining `jal rs_free`

The next remaining original site in `funcs_10.c` is
`loadLevelTextureCache` `0x80048378` (`$a0` = `$s0`
rebound at `0x80048248` to `rs_malloc(0x136C, 0)` at
`0x80048240`). Sibling remaining sites in the same file
are `freeGridCellBuffers` and `teardownGridLayerWorker`.
