# M3 s3632 — freeAllHobFiles rs_free of slot +0x8

## Work unit

Static census of `freeAllHobFiles` `jal rs_free` at
`0x80059244` (`$a0` = `0x8($s0)` of the hashed HOB slot at
`0x80139020 + index*12`). Enumerated every original
load/store of that `+0x8` word (including the
`load_hmt_and_hob` publish of kept `0x68($sp)` at
`0x80139020+index*12+0x8`, the `beq $a0, $zero` skip,
and every other store that can become this `$a0`) and
every `jal rs_free` that can receive that pointer. No
build or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw` of
HOB-slot `+0x8` (`0x80139020 + index*12 + 0x8`) and every
caller-side store that can become this `$a0`, and every
`jal rs_free` that can receive that pointer:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: releaseMeshAsset `$s5`,
load_hmt_and_hob `$s3`/`0x6C`/`0x74`, freeSubtitleOverlay
`*0x80139010`, freeTxtFile globals, loadSpriteSheetTextureFrames
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
this class (`0x80059244`). The other nine are
`loadSpriteSheetTextureFrames` `0x80055450` (closed s3627),
`loadAndRelocateAsset` `0x800555C4` (closed s3626),
`freeTxtFile` `0x800558F8`/`0x80055910` (closed s3628),
`freeSubtitleOverlay` `0x800562CC` (closed s3629),
`load_hmt_and_hob` `0x80056798`/`0x80056D60`/`0x80056D6C`
(closed s3630), and `releaseMeshAsset` `0x8005794C`
(closed s3631). None of those nine loads HOB-slot `+0x8`.
`funcs_12.c` `jal rs_free` is now exhausted.

`freeAllHobFiles` is `0x800591D4`..`0x80059294`, frame
`-0x30`. One generated caller (`endMissionCleanup`
`0x800FBA9C`). Two overlay `LOOKUP_FUNC(0x800FB9E4)` sites
in `mainGameLoop` (`0x8003E2C4`, `0x8003E388`) are mutually
exclusive teardown arms (`$s3+0x18 & 0x2000000`). Single
`jr $ra` at `0x8005928C`.

The hashed table is 96 12-byte slots at `0x80139020`
(`lui 0x8014; addiu -0x6FE0`) plus 25 bucket halfwords at
`0x801394B0` (`-0x6B50`) and freelist head `0x801394A0`
(`-0x6B60`). `initNpcBookkeepingTables` writes slot `+0x0`
next-index halfwords (`i+1`, last `0xFFFF`) and fills
buckets with `0xFFFF`; it does not write `+0x8`.

Original HOB-slot `+0x8` accesses (every function that
materializes `-0x6FE0`):

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| non-first object | `0x80056D18` | `sw $zero, 0x8($a1)` | slot `+0x8` | `bnel 0x78($sp)` delay; object index != 0 |
| object 0 publish | `0x80056D20` | `sw $t0, 0x8($a1)` | slot `+0x8` | `$t0` = `0x68($sp)` kept HOB |
| destructor load | `0x80059238` | `lw $a0, 0x8($s0)` | slot `+0x8` | only original load |
| NULL skip | `0x8005923C` | `beq $a0, $zero, L_8005924C` | `$a0` | skip `rs_free` |
| destructor | `0x80059244` | `jal rs_free` | `$a0` | no post-free NULL |

No other original `lw`/`sw` of slot `+0x8` exists.
`isHobObjectLoaded`, `walkMeshdef0List`,
`instantiateNamedMeshInstance`,
`releaseFlaggedMeshInstanceMeshes`, and
`getHobObjectByName` load slot `+0x4` (object name/header
inside the HOB) and do not load or free `+0x8`.
`walkMeshdef0List` / `instantiateNamedMeshInstance` `+0x8`
stores are mesh-instance flags, not this word.

## Object identity

### Slot `+0x8` — kept HOB file pointer

`0x68($sp)` writers in `load_hmt_and_hob`:

1. `rs_malloc($s2, 4 or 0x10)` at `0x800567EC` into `0x68`.
2. Retry `rs_malloc($s2, 0x10)` at `0x80056800` into `0x68`.
3. Packed-copy `rs_malloc(hob+0x4+4, 0x10)` at `0x8005687C`
   overwrites `0x68`; original DMA moves to `0x6C` and is
   freed at `0x80056D60` (closed s3630).

DMA dest is `0x68`. Relocate uses `0x80($sp)` = that same
kept base. Object loop `0x78($sp)` starts at 0. For object
index 0, `+0x8` stores `0x68`. For later objects,
`bnel $t0, $zero` delay-slot stores 0, so `rs_free` skips.
Zero HOB object count (`lhu 0x0(hob)==0`) jumps to
`L_80056D50` and never publishes `+0x8`; that leaks `0x68`,
not a second pointer source.

`freeAllHobFiles` walks each bucket halfword. `0xFFFF`
skips. Otherwise `$s0 = 0x80139020 + index*12`, frees
`+0x8` if nonzero, then `lhu 0x0($s0)` as the next-chain
index, `sh` that into the bucket, and continues until
`0xFFFF`. The walk collapses every bucket to `0xFFFF`.
Slots are not returned to the freelist and `+0x8` is not
NULLed. A second call therefore sees empty buckets and
does not re-free. The two `mainGameLoop` teardown arms
are mutually exclusive, so they do not run back-to-back
on the same table state.

A chain cannot hold two nonzero copies of one `0x68`:
only object index 0 of each `load_hmt_and_hob` call stores
that malloc. Distinct calls malloc distinct buffers.

## Pairing

Forty-three generated `load_hmt_and_hob` callers publish
kept `0x68` into this table. One destructor walks every
live bucket. Sequential double-free of a published word
would require a second walk of a still-linked slot; the
bucket collapse prevents that without a post-free NULL.
Failed mallocs publish NULL and the `beq $a0, $zero` skip
(and `rs_free`'s own NULL skip) return. Runtime allocator
legitimacy, freelist exhaustion (`head==0xFFFF` would
index OOB), and whether every load is later torn down
remain unproven.

## Classification

The only `jal rs_free` site that can receive this pointer
is `0x80059244`. The only original heap-pointer writer of
slot `+0x8` is `load_hmt_and_hob` `0x80056D20` storing the
matching kept-HOB `rs_malloc`. The only other original
store is `0x80056D18` zero for non-first objects. Consumers
of the hash table load `+0x4` and do not free `+0x8`. This
selects `H-NextClassComplete`. `H-NextClassGap` is refuted
at static scope. `H-NextClassUnevaluable` is not selected:
one slot layout and one heap-pointer writer.

No guard was added. Runtime allocator state, the zero-count
HOB leak of unpublished `0x68`, and pairing of every load
with this destructor remain unproven.

## Next remaining `jal rs_free`

`funcs_12.c` is exhausted. Next: `loadAssetAndIterateSubchunks`
in `funcs_11.c`: `0x8005519C` (`$a0` = `$s6` = matching
`get_asset_size_extra` `rs_malloc` at `0x80054F48` flags-4 /
`0x80054F60` flags-0 retry).
