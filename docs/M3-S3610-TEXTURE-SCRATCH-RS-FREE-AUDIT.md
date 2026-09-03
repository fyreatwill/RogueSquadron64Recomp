# M3 s3610 — remaining texture-scratch rs_free class

## Work unit

Static census of every generated original `jal rs_free` in
`loadBackdropAsset`, `initCinematicSceneAssets`, and
`buildPlayerCraftAssetTemplate`. Remaining register-then-free
scratch clones after the closed text-texture class: the two
`loadBackdropAsset` frees (`0x800AE468` of `0x60($sp)`,
`0x800AE4E0` of `0x10($s4)`), the one `initCinematicSceneAssets`
free (`0x800AE778` of `0x38($sp)`), and the one
`buildPlayerCraftAssetTemplate` free (`0x800639E4` of
`0x38($sp)`). Classified every original `sw` of each pointer and
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

Closed classes were not repeated: text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`, speech/cache
`rs_free`, destructor skipped-NULL, destructor unchecked-free,
`-0x6904` alias, remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input,
hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_28.c`: five sites. Three are
this class. The other two (`playerSnowSpeederUpdate` `0x800AD168`
of `+0xBC`, `freeEffectModelInstancePool` `0x800AE260` of the
global pool word) are later classes.

Original `jal 0x80001C98` in `funcs_14.c`: six sites. One is this
class. The other five (`loadCharTextureSet`, `loadFontAsset`,
`rebuildActiveDisplayObjectList`, `destroyLookupTable` ×2) are
later classes.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| backdrop scratch pixels | stack `0x60($sp)` | memset `0x800AE1EC` (len `0x34`); then `sw $v0` `0x800AE278` | `rs_malloc` `0x800AE270` (size `(w*h*bpp + sign_adj)>>1`) | `0x800AE468`; no post-free NULL |
| backdrop source asset | descriptor `+0x10` | `sw $v0` `0x800ADFF0`; post-free `sw $zero` `0x800AE4E8` | `load_asset` `0x800ADFE0` | `0x800AE4E0` then NULL |
| cinematic scratch pixels | stack `0x38($sp)` | ROM template copy into `$sp+0x38`; then `sw $a0` `0x800AE730` | `rs_malloc` `0x800AE718`; delay-slot `$a0 = $v0` | `0x800AE778`; no post-free NULL |
| craft scratch pixels | stack `0x38($sp)` | ROM template copy into `$sp+0x38`; then `sw $a0` `0x800639C8` | `rs_malloc` `0x800639B0`; delay-slot `$a0 = $v0` | `0x800639E4`; no post-free NULL |

`load_asset` (`0x8006488C`) calls `get_asset_size_extra`,
`rs_malloc` that size, DMA-fills, `teardownAssetDma`, and returns
`$s2` (`$v0`). That contract was classified in s3606; there is no
second pointer source.

`rs_free` itself `beq $s0, $zero` and returns, so a NULL malloc is
a skip, not a Gap.

## Remaining functions

### `loadBackdropAsset` (`0x800ADF74`) — two frees

`$s4` is `rs_malloc(0x38)` then `rs_memset` 0x38. There is one
`jr $ra`, at the function tail. Interior jumps are format-bit
selects, a `0x8($s4)==0` skip of the `+0x14` fill, a palette
stride select (`j L_800AE2A0`), a `0x8($s4)==0` skip of the copy
loop to `L_800AE464` (the scratch free), and the copy/tile loops.
None skip the scratch malloc or the `load_asset`.

`sprintf` the name into `$sp+0x20`, then `load_asset`. Delay-slot
/ fall-through `sw $v0, 0x10($s4)` is the only original store of
that word besides the post-free NULL. The descriptor's other
mallocs (`+0x14` tile indices, `+0xC` 0x30-byte object, nested
`+0xC` halfword table) are returned live; they are outside this
class.

`rs_memset($sp+0x60, 0, 0x34)` zeros the scratch struct, then
`+0x0` is replaced by `rs_malloc`. If `0x8($s4) == 0` the copy
loop is skipped to `L_800AE464`, which is the scratch free; the
malloc already ran. `zmemcpy` uses the scratch as dest. Then
`registerHmtTextureInTable($sp+0x98, $sp+0x60)`, `rs_free` of
`0x60($sp)`. Header fields of `+0x10` are still read after that
free. Then `rs_free` of `+0x10` and `sw $zero, 0x10($s4)`.

Generated callers (`setupCutsceneLevel` ×4) store `$v0` (`$s4`) at
`0x800B0B10` / `0x800B0B04` / `0x800B0B08` / `0x800B0B0C` and pass
it to `getCinematicStateSubObject` (`lw $v0, 0xC($a0)`). None
`jal rs_free` of `+0x10`. After the NULL, a later free of that
word would skip.

### `initCinematicSceneAssets` (`0x800AE518`) — one free

`$s3` is `rs_malloc(0x38)` then memset, with live child mallocs at
`+0x14`, `+0xC`, and nested `+0xC`. Those are returned; they are
outside this class. One `jr $ra`, at the tail. No branch skips the
scratch malloc.

`$sp+0x38` first receives a 0x30-byte ROM template copy from
`0x800A5BAC`. Then `rs_malloc` of the packed pixel size, delay-slot
`addu $a0, $v0`, `rs_memset` fill 0xFF, and `sw $a0, 0x38($sp)`
overwrites the template's first word. Last writer before the free
is that malloc store. `registerHmtTextureInTable($sp+0x10,
$sp+0x38)` then `rs_free` of `0x38($sp)`. Stack `0x60($sp)` /
`0x62($sp)` are width/height halfwords of the texture header, not
the freed pointer.

The single generated caller is `cinematicInitializer`. It keeps
`$v0` (`$s3`) and loads `+0xC`, not the scratch.

### `buildPlayerCraftAssetTemplate` (`0x800638C4`) — one free

`$s1` is `rs_malloc(0x34)` then memset; that object is returned
live. One `jr $ra`, at the tail. No branch skips the scratch
malloc.

`$sp+0x38` first receives a 0x30-byte ROM template copy from
`0x8003B7F4`. Then `rs_malloc` of `w*h`, delay-slot `addu $a0,
$v0`, `rs_memset` fill 0xFF, and `sw $a0, 0x38($sp)` overwrites
the template's first word. Last writer before the free is that
malloc store. `registerHmtTextureInTable($sp+0x10, $sp+0x38)`
then `rs_free` of `0x38($sp)`. The later `sw $zero, 0x10($s1)`
initializes the returned object's `+0x10`, not the freed scratch.

The single generated caller is `initPlayerSlotAnimationChannelFull`.
It stores `$v0` (`$s1`) at `+0x44C` and writes `+0x2F`; it does not
retain the scratch.

### `registerHmtTextureInTable` (`0x80022B90`) — does not free these

Saves `a0`/`a1`, then `parseHmtMaterials`. It has no
`jal rs_free`. Helpers used on these paths (`sprintf`,
`rs_strcpy`, `rs_memset`, `zmemcpy`, `getCinematicStateSubObject`)
likewise do not free the scratch pixel word or the `load_asset`
pointer.

## Double-free / non-allocator edges

Scratch pixels live on the callee stack. Each function rebuilds
those slots on the next call before the next free.

`+0x10` is NULLed after its one free. Callers read `+0xC`/`+0x14`,
not `+0x10`. Sequential double-free of stack scratch is blocked by
rebuild-before-next-call.

Re-init without shutdown, malloc-size zero, and allocator failure
are the same unproven runtime edges s3604–s3609 left open, not a
second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected: the four
pointers are the two stack scratch words, the descriptor `+0x10`
asset, and the cinematic/craft stack scratch words.
