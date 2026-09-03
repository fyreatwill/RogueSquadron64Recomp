# M3 s3626 — loadAndRelocateAsset load_asset rs_free

## Work unit

Static census of `loadAndRelocateAsset` `jal rs_free` at
`0x800555C4` (`$a0` = `$s1` = `load_asset` return copied at
`0x800554F8`). Enumerated every original load/store of that
pointer (including the 8-iter relocate walk that uses
`$s1+4` as a base and the `0x20`/`0x24` pointer-add stores)
and every `jal rs_free` that can receive it. Classified the
pointer's writer and whether a free can run on a
non-allocator or already-freed value. No build or runtime
run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of the `load_asset` return kept in `$s1` (and any store of
it to a global or stack word) and every `jal rs_free` that
can receive it:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadExplosionTextures
load_asset, freeEffectAssetBuffers globals, loadSkyHorizonHob
stack scratch, cinematicSplineWalkerNpcHandler nested
0xF00/0x2B44, spawnCutsceneObjectsFromList 0x6C, NPC
allocateAndInit destructor, player-craft `+0xBC`,
playerAtStUpdate 0xA4/0xBC, actor `+0x4C`,
tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`,
speech/cache `rs_free`, destructor skipped-NULL, destructor
unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table,
pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_12.c`: 10 sites. One is
this class (`0x800555C4`). The other nine are
`loadSpriteSheetTextureFrames` `0x80055450` (next remaining),
`freeTxtFile` `0x800558F8`/`0x80055910`,
`freeSubtitleOverlay` `0x800562CC`,
`load_hmt_and_hob` `0x80056798`/`0x80056D60`/`0x80056D6C`,
`releaseMeshAsset` `0x8005794C`, and
`freeAllHobFiles` `0x80059244`. None of those nine receives
the `loadAndRelocateAsset` `$s1`.

`loadAndRelocateAsset` is `0x800554D8`..`0x800555E8`. Ten
generated callers. Single `jr $ra` at `0x800555E0`, after
the free. Both the `$s2==0` and `$s2!=0` name arms reach
`registerHmtTextureInTable` and the free.

## Pointer writer and interior stores

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| load_asset | `0x800554F0`/`0x800554F8` | `jal load_asset($a0)`; `addu $s1, $v0` | `$s1` | only heap-pointer writer |
| callee spill | `0x800554F4` | `sw $s1, 0x3C($sp)` | old `$s1` | pre-copy spill of the caller's `$s1`, not the malloc |
| relocate base | `0x800554FC` | `addiu $a1, $s1, 0x4`; `$a2=$v1=$a1` | `$s1+4` | header base; not a store of `$s1` |
| 8-iter walk | `0x8005550C`..`0x80055528` | `lw`/`addu $a2`/`sw` at `$v1`, `$v1+=4`, `slti 0x8` | header `+0x00..+0x1C` | relocates 8 interior words into the buffer |
| extra +0x20 | `0x8005552C`..`0x80055538` | `lw`/`addu $a2`/`sw 0x20($a1)` | header `+0x20` = `$s1+0x24` | same relocate into the buffer |
| extra +0x24 | `0x8005553C`..`0x80055548` | `lw`/`addu $a2`/`sw 0x24($a1)` | header `+0x24` = `$s1+0x28` | same relocate into the buffer |
| flags | `0x80055574`/`0x80055580` | `lhu 0x32($s1)`; `or $s0`; `sh` | header `+0x2E` | OR of caller `$a2` into the asset flags |
| name override | `0x8005559C` | `sw $s0, 0x28($s1)` when `$s2!=0` | header `+0x24` | stack `sp+0x24`; no generated caller takes this arm |
| name copy | `0x800555A4` | `lw $a1, 0x28($s1)` when `$s2==0` | header `+0x24` | consumer of the relocated name pointer |
| register | `0x800555B4`/`0x800555B8` | `jal registerHmtTextureInTable(sp+0x10, $s1+4, 0)` | `$s1+4` | copy consumer; does not store `$s1` |
| destructor | `0x800555C0`/`0x800555C4` | `addu $a0, $s1`; `jal rs_free` | `$s1` | destructor; no store; no post-free NULL |
| restore | `0x800555D8` | `lw $s1, 0x3C($sp)` | caller's `$s1` | after the free |

The 8-iter walk plus the `0x20`/`0x24($a1)` stores are the
inlined body of `full_header_image_offset_convert`
(`0x80055488`). They write relocated interior pointers
*into* the malloc buffer. They are not a second writer of
`$s1`.

`load_asset` (`0x8006488C`) calls `get_asset_size_extra`,
`rs_malloc` that size, DMA-fills, `teardownAssetDma`, and
returns `$s2` (`$v0`). That contract was classified in
s3606/s3611; there is no second pointer source. `rs_free`
itself `beq $s0, $zero` and returns, so a NULL malloc is a
skip, not a Gap. The relocate walk dereferences `$s1+4`
before the free, so a NULL return would fault first; that
is the same unproven allocator-failure edge s3604–s3625
left open.

No `jal` clobbers `$s1` between `addu $s1, $v0` and
`rs_free`: `rs_strncpy` and `registerHmtTextureInTable`
preserve callee-saved `$s1`. The delay slot of the free
captures the texture id in `$s0`; the function returns
`$s0 & 0xFFFF`, not the heap pointer.

## Register / copy consumers (not the heap pointer)

`registerHmtTextureInTable` (`0x80022B90`) keeps `$a1`
(`$s1+4`) in `$t1` and calls `parseHmtMaterials` with that
header. `parseHmtMaterials` (`0x80022A00`) reads header
halfwords/bytes, passes interior pointers
(`header+0x20`, `header+0x24`, `header+0x30`) to
`loadTextureToMemory`, and publishes a texture-id halfword
into the material array. It does not store `$s1` or
`$s1+4`, and it has no `jal rs_free`.

`loadTextureToMemory` (`0x8001F954`) copies `$a0` (header)
into `$s7` and the relocated `header+0x20` word into `$s5`.
Its persistent stores are texture-table dest pointers and
the `0x8011A7D0` bump cursor, not `$s7`. It has no
`jal rs_free`. `parseImageFile` (`0x8001EB24`) is the pixel
decode callee; it has no `jal rs_free` and no `rs_malloc`.

The `$s2!=0` arm (`sw sp+0x24, 0x28($s1)`) overwrites the
relocated name pointer with a stack address before
register. Every generated caller passes `$a1=0`, so that
arm is original-dead. The free still receives `$s1`.

## Callers

All ten generated `jal 0x800554D8` sites pass `$a1=0`. They
keep only the returned texture-id halfword. None
`jal rs_free` of `$v0` or of `$s1`.

| Function | PC | `$a0` name | `$a2` | `$v0` store |
|---|---|---|---|---|
| `loadWeaponsHobObjects` | `0x8005E880` | `0x8003B168` | 0 | `sh` `0x80139738` (`-0x68C8`) |
| `loadTieBomberSprite` | `0x8005ECFC` | `0x8003B168` | 0 | `sh` `0x80139738` |
| `initHudStruct` | `0x800C0574` | `0x800A6384` | 0 | `sh 0x8($s2)` |
| `initHudStruct` | `0x800C0698` | `$sp+0x18` | 0 | `sh 0xE($s2)` |
| `initHudStruct` | `0x800C0C64` | `$sp+0x18` | 0 | `sh 0x10($s2)` |
| `initHudStruct` | `0x800C0E1C` | `$sp+0x18` | 0 | `sh 0x12($s2)` |
| `initHudStruct` | `0x800C0FD8` | `0x800A643C` | 0 | `sh 0x38($s2)` (next jal delay) |
| `initHudStruct` | `0x800C0FF0` | `0x800A6448` | 0 | `sh 0x3A($s2)` |
| `initializeRadar` | `0x800C4634` | `0x800A673C` | 0 | `sh 0x85A($s2)` |
| `configurePlayerSecondaryWeaponHud` | `0x800FBEB4` | `*($s2)` table | `0x2000` | `sh 0xA($s3)` |

A second `loadAndRelocateAsset` mallocs, relocates, registers,
and frees a new buffer; the previous buffer is already freed
at the first return.

## Classification

The only `jal rs_free` that can receive this pointer is
`0x800555C4`, and `$a0` is the matching `load_asset`
`rs_malloc`. The 8-iter / `0x20` / `0x24` stores relocate
interior words into that buffer; register copies pixels and
keeps a texture id. No original non-allocator writer exists,
and no sibling free can see `$s1`. This selects
`H-NextClassComplete`. `H-NextClassGap` is refuted at static
scope. `H-NextClassUnevaluable` is not selected: one original
heap-pointer writer, never stored.

No guard was added. Runtime allocator state, DMA fill, and
relocate-offset legitimacy remain unproven.

## Next remaining `jal rs_free`

`loadSpriteSheetTextureFrames` `0x80055450` in `funcs_12.c`.
`$s2` is the inlined `get_asset_size_extra` / `rs_malloc`
return at `0x8005524C`; an 8-iter relocate walk uses
`$s2+4` as base, then a frame loop calls
`registerHmtTextureInTable` and `rs_free($s2)`.
