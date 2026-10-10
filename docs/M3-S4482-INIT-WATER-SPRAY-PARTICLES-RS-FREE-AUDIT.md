# M3 s4482 — initWaterSprayParticles rs_free of the wtrspray_ANM buffer

## Work unit

Static census of the one original `jal rs_free` in
`initWaterSprayParticles` (`0x80072CF0`, size `0x1D4`), at
`0x80072E40`. The instruction before the jal is
`addu $a0, $s3, $zero` at `0x80072E3C`. The delay slot is
`addu $s0, $v0, $zero` at `0x80072E44`. It runs before the
call, so `$s0` receives `registerHmtTextureInTable`'s
texture id, not `rs_free`'s return, and it does not write
`$a0`. No build or runtime run was performed.
`walkDatTreeAndCollectSubtypes` (s4481) was not re-audited.

The discriminator was every original assignment of `$s3`
from the prologue through the free, every callee
`jal rs_free`, and every caller argument:

- H-NextClassGap: `$s3` can be a non-allocator value, or a
  pointer a sibling already freed, with the writer named.
- H-NextClassComplete: `$s3` is the matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates closed `0x80072B8C` and this site in
`funcs_18.c`, still locates `0x8006DA28` and `0x8006F378`
in `funcs_17.c`, and still locates `0x8006C8C4` (also
`0x8006B814`, `0x8006C4A8`, `0x8006C650`) in `funcs_16.c`.
The ROM word `0x0C000726` matches `0x8006B814`,
`0x8006C8C4`, `0x80005268`, `0x8006DA28`, `0x8006F378`,
`0x80072B8C`, and `0x80072E40`. A scan that missed
`0x80072B8C` would have been invalid. ROM and the generated
listing agree on the free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_18.c`, `0x80072E40` | `$s3` | `addu $a0, $s3`; delay writes `$s0` | sole free; the `load_asset` / `rs_malloc` return of `gnrc_stuff/wtrspray_ANM` |

The function has no branch other than `jal` and the final
`jr $ra`. The free is on the only path. `$s3` is assigned
once before it: `addu $s3, $v0, $zero` at `0x80072DD4`,
after `jal load_asset` at `0x80072DCC`. That jal's delay
slot is `addu $a0, $s1, $zero` and does not write `$v0`.
`sw $s3, 0x44($sp)` at `0x80072D50` saves the incoming
`$s3` and does not assign it. `lw $s3, 0x44($sp)` at
`0x80072E94` is after the free and restores that incoming
value. No instruction stores `$s3` after `0x80072DD4`, so
the malloc pointer is never written to memory.

Incoming `$a0` is overwritten at `0x80072CF4` (`lui $a0,
0x8004`) before any use. A caller argument cannot reach
the free.

## What load_asset returns

`load_asset` (`0x8006488C`) is straight-line. It calls
`get_asset_size_extra` (`0x80004D5C`), then `jal rs_malloc`
at `0x800648C0` with flags 0 (`addu $a1, $zero`). `$s2`
takes that `$v0` at `0x800648DC`. `findAssetAcrossSegments`,
`setupAssetDma`, and `teardownAssetDma` follow.
`addu $v0, $s2` at `0x80064914` is the only return.
`load_asset` saves the caller's `$s3` at `0x24($sp)` and
restores it at `0x8006491C`. Its own `$s3` is the size, and
`sw $s3, 0x10($sp)` at `0x800648FC` passes that size into
`setupAssetDma`. None of those four helpers contains
`jal rs_free`. The name in `$s1` is `0x8003CF20`,
`gnrc_stuff/wtrspray_ANM`.

## Callees while `$s3` holds the pointer

`full_header_image_offset_convert` (`0x80055488`) is a
leaf. Both `$a0` and `$a1` are `$s3+4`. It rewrites eight
words and the words at `+0x20` and `+0x24` inside the
buffer. It does not write `$s3` and has no `jal`.

`registerHmtTextureInTable` (`0x80022B90`) receives the
stack descriptor at `$sp+0x10`, the header `$s3+4`, and
`$a2 = 0`. It does not write `$s3` and has no
`jal rs_free`. It calls `parseHmtMaterials`.

`parseHmtMaterials` does not write `$s3` and has no
`jal rs_free`. Its jals are `loadTextureToMemory` and
`rs_strncpy`. `rs_strncpy` (`0x80007640`) is a leaf and
does not write `$s3`.

`loadTextureToMemory` saves `$s3` at `0x8001F968` and
restores it at `0x8001FE58`. It has no `jal rs_free`. Its
callees are `rs_strncmp`, `rs_strncpy`,
`decodeRdpSizeFlags`, `parseImageFile` (twice), and
`packTlutEntriesRgba5551` (twice). `rs_strncmp`,
`decodeRdpSizeFlags`, and `packTlutEntriesRgba5551` do not
write `$s3` and do not jal. `parseImageFile` saves `$s3`
at `0x8001EB5C` and restores it at `0x8001F938`, after its
only jal, `swizzleTextureRowsToTmem` (`0x8001EED8`). That
swizzle is a leaf: no jal, no `$s3` write.

No function in that tree contains `jal rs_free`. None
returns with the caller's `$s3` changed.

## Other pointers in the same function

These are not `$s3`:

| Value | Source | Where it goes |
|---|---|---|
| `$s6` | `walkMeshdef0List("wtrspray")` `$v0`, captured in the delay slot of `findTextureByName` | `releaseMeshAsset` after this free |
| `$s5` | `findTextureByName("waterwhite_1")` low halfword | `releaseTextureLutEntry` before `load_asset`, then the material-flag `$a1` |
| `$s0` after the free's delay | `registerHmtTextureInTable` `$v0` | material-flag `$a2`; a texture id |
| `loadAssetIntoNewSlot` `$v0` | a later load of the same ANM name | `setPoolEntryPhaseAndMarkActive`; not this free |

`load_hmt_and_hob("gnrc_stuff/wtrspray")` returns before
`$s3` is assigned. The three zeroed records at
`0x8013A8C0`, `0x8013A8F0`, and `0x8013A920` are not the
heap pointer. The descriptor copied onto the stack is the
ROM record at `0x8003CF10` (`waterwhite_1`), not the
allocation.

## Callers

One direct `jal 0x80072CF0`, at `0x80079A80` in
`initWaterSprayEffectAndSfx`. The delay slot is `nop`.
The whole ROM contains that one jal encoding
(`0x0C01CB3C`), no data word `0x80072CF0`, and no
`lui 0x8007` / `addiu`/`ori 0x2CF0` pair. There is no
indirect call. The wrapper has no `jal rs_free`.

The wrapper itself is called from `initMission`
(`0x800FA660`, `.ovl.mission`),
`initMenuBackdropAndPickRandom` (`0x800C5758`,
`.ovl.menu`), and `load_cutscene` (`0x800A6868`,
`.ovl.cinematic`). Those calls return after this function
has already freed the buffer, and the buffer was never
stored.

`rs_free` branches away when `$a0 == 0` (`beq` at
`0x80001CA4`). A NULL `rs_malloc` return is the same
unproven allocator-failure edge left open by s3604–s4481,
not a second pointer identity. `full_header` loads
`0($a0)` at `0x80055490` before this jal, so a NULL return
faults first. A second call of this function mallocs and
frees a new buffer. `loadAssetIntoNewSlot` of the same
name is a separate allocation after this free.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static
scope: the only value in `$s3` at `0x80072E40` is the
`load_asset` `rs_malloc` of `gnrc_stuff/wtrspray_ANM`, no
callee frees it, and it is not stored where a sibling
could free it. H-NextClassUnevaluable is not selected.
Runtime allocator and DMA-fill legitimacy remain unproven.
No guard was added.

`funcs_18.c` has no unclassified `jal rs_free` left. The
next unaudited site in address order is
`downscaleImageHalfResBoxFilter` at `0x8007A814` (entry
`0x8007A260`, size `0x60C`, `funcs_19.c`). `$a0` is `$s5`
(`addu $a0, $s5` at `0x8007A7F8`). The delay slot
`sb $v1, 1($v0)` at `0x8007A818` does not write `$a0`.
The only `$s5` write before that free is
`addu $s5, $v0` at `0x8007A320`, after `jal rs_malloc` at
`0x8007A318`.
