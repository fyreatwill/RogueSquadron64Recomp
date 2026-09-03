# M3 s3627 — loadSpriteSheetTextureFrames inlined-malloc rs_free

## Work unit

Static census of `loadSpriteSheetTextureFrames` `jal rs_free` at
`0x80055450` (`$a0` = `$s2` = inlined `get_asset_size_extra` /
`rs_malloc` return copied at `0x8005524C`). Enumerated every
original load/store of that pointer (including the 8-iter
relocate walk that uses `$s2+4` as a base, the frame loop that
calls `registerHmtTextureInTable`, and any store of `$s2` to a
global or stack word) and every `jal rs_free` that can receive
it. Classified the pointer's writer and whether a free can run
on a non-allocator or already-freed value. No build or runtime
run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of the `rs_malloc` return kept in `$s2` (and any store of it
to a global or stack word) and every `jal rs_free` that can
receive it:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadAndRelocateAsset
load_asset, loadExplosionTextures load_asset,
freeEffectAssetBuffers globals, loadSkyHorizonHob stack
scratch, cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
spawnCutsceneObjectsFromList 0x6C, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor `+0x4C`, tickMultiPartVoiceLine, freeModelViewerMeshChain,
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
this class (`0x80055450`). The other nine are
`loadAndRelocateAsset` `0x800555C4` (closed s3626),
`freeTxtFile` `0x800558F8`/`0x80055910` (next remaining),
`freeSubtitleOverlay` `0x800562CC`,
`load_hmt_and_hob` `0x80056798`/`0x80056D60`/`0x80056D6C`,
`releaseMeshAsset` `0x8005794C`, and
`freeAllHobFiles` `0x80059244`. None of those nine receives
the `loadSpriteSheetTextureFrames` `$s2`.

`loadSpriteSheetTextureFrames` is `0x800551D8`..`0x80055488`
(size `0x2B0`). One generated caller. Single `jr $ra` at
`0x80055480`, after the free. The `blez $s4` skip of the
frame loop still reaches the free.

## Pointer writer and interior stores

The first ~0xA8 bytes are the inlined body of `load_asset`
(`0x8006488C`): `get_asset_size_extra`, `rs_malloc` that
size with flags 0, `findAssetAcrossSegments`, `setupAssetDma`
dest=`$s2`, `teardownAssetDma`. That contract was classified
in s3606/s3611/s3626; there is no second pointer source.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| name copy | `0x800551E0` | `addu $s2, $a0` | `$s2` | caller name; overwritten before any free |
| size | `0x80055220`/`0x80055228` | `jal get_asset_size_extra`; `addu $s3, $v0` | `$s3` | size, not the pointer |
| rs_malloc | `0x80055230`/`0x8005524C` | `jal rs_malloc($s3, 0)`; `addu $s2, $v0` | `$s2` | only heap-pointer writer |
| DMA dest arg | `0x80055274` | `sw $s2, 0x14($sp)` | callee stack | dest arg to `setupAssetDma`; not a persistent store |
| DMA slot dest | `0x80004F04` | `sw dest, 0x24($a2)` inside `setupAssetDma` | command slot `0x80111100+40*i+0x24` | transient fill dest; `teardownAssetDma` does not load or `jal rs_free` it |
| relocate base | `0x80055284` | `addiu $a1, $s2, 0x4`; `$a2=$v1=$a1` | `$s2+4` | header base; not a store of `$s2` |
| 8-iter walk | `0x80055294`..`0x800552B0` | `lw`/`addu $a2`/`sw` at `$v1`, `$v1+=4`, `slti 0x8` | header `+0x00..+0x1C` | relocates 8 interior words into the buffer |
| extra +0x20 | `0x800552B4`..`0x800552C0` | `lw`/`addu $a2`/`sw 0x20($a1)` | header `+0x20` = `$s2+0x24` | same relocate into the buffer |
| extra +0x24 | `0x800552C4`..`0x800552D0` | `lw`/`addu $a2`/`sw 0x24($a1)` | header `+0x24` = `$s2+0x28` | same relocate into the buffer |
| width | `0x80055324` | `sh $s6, 0x2E($s2)` | header `+0x2A` | per-frame width from caller `$a2` |
| flags | `0x800553E0`/`0x800553F4` | `lhu 0x32($s2)`; `or` 6th arg; `sh` | header `+0x2E` | OR of caller flags |
| name copy dest | `0x80055418` | `lw $a0, 0x28($s2)`; `jal rs_strcpy` | relocated name pointer | interior consumer; `rs_strcpy` only writes bytes at `$a0` |
| register | `0x80055428`/`0x8005542C` | `jal registerHmtTextureInTable(sp+0x18, $s2+4, 0)` | `$s2+4` | copy consumer; does not store `$s2` |
| image advance | `0x80055438`/`0x80055440` | `lw 0x4($s2)`; `addu $s1`; `sw 0x4($s2)` | header `+0x00` | stride walk of the relocated image pointer |
| destructor | `0x80055450`/`0x80055454` | `jal rs_free`; `addu $a0, $s2` | `$s2` | destructor; no store; no post-free NULL |
| restore | `0x80055474` | `lw $s2, 0x48($sp)` | caller's `$s2` | after the free |

The 8-iter walk plus the `0x20`/`0x24($a1)` stores are the
inlined body of `full_header_image_offset_convert`
(`0x80055488`). They write relocated interior pointers
*into* the malloc buffer. They are not a second writer of
`$s2`.

`rs_free` itself `beq $s0, $zero` and returns, so a NULL
malloc is a skip, not a Gap. The relocate walk dereferences
`$s2+4` before the free, so a NULL return would fault first;
that is the same unproven allocator-failure edge s3604–s3626
left open.

No `jal` clobbers `$s2` between `addu $s2, $v0` and
`rs_free`: `findAssetAcrossSegments`, `setupAssetDma`,
`teardownAssetDma`, `sprintf`, `rs_strcpy`, and
`registerHmtTextureInTable` preserve callee-saved `$s2`.
The function does not return the heap pointer; `$v0` after
the free is `rs_free`'s return.

## Format jump table (not a skip of the free)

`lhu 0x32($s2)` nibble 0..5 indexes `0x8003AD38`. All six
targets stay inside the function and join `L_800553AC` /
`L_800553B0` before the frame loop:

| Nibble | Target | Stride `$s1` |
|---|---|---|
| 0 | `0x80055398` | `(lh 0x2C($s2)+1) >> 1` |
| 1 | `0x8005538C` | `lh 0x2C($s2)` |
| 2 | `0x80055344` | `lh 0x2C($s2) << 1` |
| 3 | `0x80055350` | `0x8000` set: `<< 2`; else `* 3` |
| 4 | `0x8005537C` | `0x8000` set: `lh 0x2C`; else `(lh+1)>>1` |
| 5 | `0x8005538C` | `lh 0x2C($s2)` |

Nibble `>= 6` sets `$s1 = 0` at `0x800553A8` and joins the
same path. `blez $s4` at `0x800553F0` skips the frame loop
and still `jal rs_free`.

## Register / copy consumers (not the heap pointer)

The frame loop (`$s0 = 0 .. $s4-1`, `$s4` = `lh 0x2E / $a2`
clamped by the 5th arg) does:

- `sprintf(sp+0x2C, "%s_%d", $fp, $s0)` at `0x8005540C`
- `rs_strcpy(*(0x28($s2)), sp+0x2C)` at `0x8005541C`
- `registerHmtTextureInTable(sp+0x18, $s2+4, 0)` at `0x8005542C`
- `sh $v0, 0x0($s5)` then `$s5 += 2` (caller output halfwords)
- `sw 0x4($s2) += $s1` (advance the relocated image pointer)

`registerHmtTextureInTable` (`0x80022B90`) was classified in
s3626: it does not store `$s2` or `$s2+4`, and it has no
`jal rs_free`. `rs_strcpy` (`0x8000761C`) only writes bytes
at its dest; dest is the relocated name pointer, not `$s2`.
`sprintf` writes the callee stack.

`setupAssetDma` (`0x80004E70`) stores dest in a command slot
at `+0x24` and, with `$a1=0`, blocks until the fill
completes. `teardownAssetDma` (`0x80004C70`) posts cmd
`0x8001` and waits; it has no `jal rs_free` and does not
load slot `+0x24`. That dest word is the same transient DMA
fill target `load_asset` uses; it is not a second owner.

## Callers

One generated `jal 0x800551D8`: `initHudStruct`
(`0x800C0084`, jal `0x800C0910`).

| Arg | Value |
|---|---|
| `$a0` | `$sp+0x18` copy of `ov/ov_font` (`0x800A6394`), last byte patched |
| `$a1` / `$fp` | `o_fn` (`0x800A63A0`), sprintf prefix |
| `$a2` / `$s6` | `0xA` or `0x14` (manifest-type width) |
| `$a3` / `$s5` | HUD `+0x18` halfword array |
| 5th / `$s7` | `0x3E8` (max-frame clamp) |
| 6th | `0` (flags OR) |

The caller does not keep `$v0` and does not `jal rs_free` of
`$s2`. Texture-id halfwords are stored into HUD `+0x18`
during the frame loop. The next instruction is
`getBootConfigField12`.

## Classification

The only `jal rs_free` that can receive this pointer is
`0x80055450`, and `$a0` is the matching inlined `rs_malloc`.
The 8-iter / `0x20` / `0x24` stores relocate interior words
into that buffer; register copies pixels and keeps texture
ids. No original non-allocator writer exists, and no sibling
free can see `$s2`. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: one original
heap-pointer writer, never stored to a global or object
field.

No guard was added. Runtime allocator state, DMA fill, and
relocate-offset legitimacy remain unproven.

## Next remaining `jal rs_free`

`freeTxtFile` `0x800558F8` / `0x80055910` in `funcs_12.c`.
`$a0` is `*0x8009ECA0` then `*0x8009ECA8` (`lui 0x800A` +
`-0x1360` / `-0x1358`), each NULL-skipped, then
`teardownAssetDma` of `*0x8009ECA4` when that word is not
`-1`.
