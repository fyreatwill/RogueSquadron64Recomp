# M3 s3609 — remaining text-texture rs_free class

## Work unit

Static census of every generated original `jal rs_free` in
`loadNamedTextureDescriptor`, `allocTextRenderTarget`, and
`bridgeLoadShipBlueprints`. Remaining `funcs_30.c` frees after the
closed format-message class: the two `loadNamedTextureDescriptor`
frees (`0x800B3244`, `0x800B32BC`), the one `allocTextRenderTarget`
free (`0x800B354C`), and the one `bridgeLoadShipBlueprints` free
(`0x800B17C8`). Classified every original `sw` of each pointer and
whether a free can run on a non-allocator or already-freed value.
No build or runtime run was performed.

The discriminator was the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: format-message `rs_free`,
speech-file `rs_free`, speech/cache `rs_free`, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`,
`+0x60`, MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_30.c`: nine sites. Four are this
class. The other five (`tickFormatMessageWorker` /
`disposeFormatMsgQueueMember`) were closed in s3608.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| named scratch pixels | stack `0x60($sp)` | memset `0x800B2FC8` (len `0x34`); then `sw $v0` `0x800B3054` | `rs_malloc` `0x800B304C` (size `(w*h*bpp + sign_adj)>>1`) | `0x800B3244`; no post-free NULL |
| named source asset | descriptor `+0x10` | `sw $v0` `0x800B2DCC`; post-free `sw $zero` `0x800B32C8` | `load_asset` `0x800B2DBC` (`rs_malloc` of `get_asset_size_extra`) | `0x800B32BC` then NULL |
| text-target scratch pixels | stack `0x38($sp)` | ROM template copy into `$sp+0x38`; then `sw $a0` `0x800B3504` | `rs_malloc` `0x800B34EC`; delay-slot `$a0 = $v0` | `0x800B354C`; no post-free NULL |
| blueprint asset `$s1` | `$s1` | `addu $s1, $v0` `0x800B1724` each of 9 loop iters | `load_asset` `0x800B171C` | `0x800B17C8` (`addu $a0, $s1`); no post-free NULL |

`load_asset` (`0x8006488C`) calls `get_asset_size_extra`,
`rs_malloc` that size, DMA-fills, `teardownAssetDma`, and returns
`$s2` (`$v0`). That contract was classified in s3606; there is no
second pointer source.

`rs_free` itself `beq $s0, $zero` and returns, so a NULL malloc is
a skip, not a Gap.

## Remaining functions

### `loadNamedTextureDescriptor` (`0x800B2D50`) — two frees

`$s4` is `rs_malloc(0x38)` then `rs_memset` 0x38. There is one
`jr $ra`, at the function tail. The only interior jump
(`0x800B306C` → `L_800B307C`) is a stride select after the scratch
malloc.

`sprintf` the name, then `load_asset`. Delay-slot /
fall-through `sw $v0, 0x10($s4)` is the only original store of that
word besides the post-free NULL. The descriptor's other mallocs
(`+0x14` tile indices, `+0xC` 0x30-byte object, nested `+0xC`
halfword table) are returned live; they are outside this class.

`rs_memset($sp+0x60, 0, 0x34)` zeros the scratch struct, then
`+0x0` is replaced by `rs_malloc`. If `0x8($s4) == 0` the copy
loop is skipped to `L_800B3240`, which is the scratch free; the
malloc already ran. `zmemcpy` uses the scratch as dest. Then
`registerHmtTextureInTable($sp+0x98, $sp+0x60)`, `rs_free` of
`0x60($sp)`, then `rs_free` of `+0x10` and `sw $zero, 0x10($s4)`.

Generated callers (`menuControllerInput`, `buildHudAmmoReadout` ×2,
`createMenuTextLabels` ×2, `postLevelSaveInit`,
`runMenuShipSelectScreen`, `menuSubtype02Handler`) pass `$v0` to
`getStructField0xC` (`lw $v0, 0xC($a0)`) and consume `+0x14`. None
`jal rs_free` of `+0x10`. After the NULL, a later free of that word
would skip.

### `allocTextRenderTarget` (`0x800B32F4`) — one free

`$s4` is `rs_malloc(0x38)` then memset, with live child mallocs at
`+0x14`, `+0xC`, and nested `+0xC`. Those are returned; they are
outside this class. One `jr $ra`, at the tail. No branch skips the
scratch malloc.

`$sp+0x38` first receives a 0x30-byte ROM template copy from
`0x800A5C7C`. Then `rs_malloc` of the packed pixel size, delay-slot
`addu $a0, $v0`, `rs_memset` fill 0xFF, and `sw $a0, 0x38($sp)`
overwrites the template's first word. Last writer before the free
is that malloc store. `registerHmtTextureInTable($sp+0x10,
$sp+0x38)` then `rs_free` of `0x38($sp)`.

Generated callers (`initTextTextureTarget`,
`spawnMenuListItemSprite`) keep `$v0` (`$s4`), not the scratch.

### `bridgeLoadShipBlueprints` (`0x800B165C`) — one free

`$s4` walks 0..8 (`sltiu $s4, 9` after each free). Each iteration:
`sprintf` a name from the copied ROM table, `load_asset`,
`$s1 = $v0`, `$s0 = $s1+4` as the image payload,
`full_header_image_offset_convert`, `rs_strcpy`,
`registerHmtTextureInTable($sp+0x58, $s0)`, fill a 0x30-byte slot
at `$s2`, `findLookupEntryByKey`, then `rs_free($s1)`. The next
iteration overwrites `$s1` from a new `load_asset` after that free.
One `jr $ra`, at the tail.

The single generated caller is `initCraftSelectScreen`. It does not
retain `$s1`.

### `registerHmtTextureInTable` (`0x80022B90`) — does not free these

Saves `a0`/`a1`, then `parseHmtMaterials` → `loadTextureToMemory`.
The upload copies from a KSEG0 source (`asset+0xC` / palette) into
the texture heap via `0x8001E36C` and does not `jal rs_free` of the
scratch pixel word or the `load_asset` pointer. Helpers used on
these paths (`sprintf`, `rs_strcpy`, `rs_memset`, `zmemcpy`,
`full_header_image_offset_convert`, `findLookupEntryByKey`,
`getStructField0xC`) likewise do not free them.

## Double-free / non-allocator edges

Scratch pixels live on the callee stack. `loadNamedTextureDescriptor`
and `allocTextRenderTarget` rebuild those slots on the next call
before the next free. `loadBackdropAsset` / `initCinematicSceneAssets`
/ `buildPlayerCraftAssetTemplate` have the same `0x60($sp)` /
`0x38($sp)` / `0x10($s4)` shape on *their* stacks; they are a later
class, not a sibling free of these objects.

`+0x10` is NULLed after its one free. Callers read `+0xC`/`+0x14`,
not `+0x10`. Sequential double-free of `$s1` is blocked by the
per-iter `load_asset` overwrite.

Re-init without shutdown, malloc-size zero, and allocator failure
are the same unproven runtime edges s3604–s3608 left open, not a
second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected: the four
pointers are the two stack scratch words, the descriptor `+0x10`
asset, and the per-iter `$s1` asset.
