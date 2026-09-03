# M3 s3611 — remaining load_asset-then-free clones

## Work unit

Static census of every generated original `jal rs_free` in
`hangarLoadShadows` and `loadFontAsset`. Remaining load_asset-then-free
clones after the closed texture-scratch class: the one
`hangarLoadShadows` free (`0x800AEA94` of `$s4`) and the one
`loadFontAsset` free (`0x80061C24` of `$s0`). Classified every original
`sw` of each pointer and whether a free can run on a non-allocator or
already-freed value. No build or runtime run was performed.

The discriminator was the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: texture-scratch `rs_free`,
text-texture `rs_free`, format-message `rs_free`, speech-file
`rs_free`, speech/cache `rs_free`, destructor skipped-NULL,
destructor unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_29.c`: one site. It is this class.

Original `jal 0x80001C98` in `funcs_14.c`: six sites. One is this
class. The other five (`loadCharTextureSet`,
`rebuildActiveDisplayObjectList`, `destroyLookupTable` ×2, and the
s3610 craft-scratch free) are later or already-closed classes.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| hangar shadow asset | `$s4` | `addu $s4, $v0` `0x800AEA0C` | `load_asset` `0x800AEA04` | `0x800AEA94`; no post-free NULL |
| font glyph asset | `$s0` | `addu $s0, $v0` `0x80061B6C` each of 6 loop iters | `load_asset` `0x80061B64` | `0x80061C24`; no post-free NULL |

Neither pointer is stored to a global or object field. The only
`sw` involving a derived address is `loadFontAsset`'s
`sw $s0+0xC, 0x78($sp)` (`0x80061BCC`), an interior payload pointer
consumed by `registerHmtTextureInTable` before the free.

`load_asset` (`0x8006488C`) calls `get_asset_size_extra`,
`rs_malloc` that size, DMA-fills, `teardownAssetDma`, and returns
`$s2` (`$v0`). That contract was classified in s3606; there is no
second pointer source.

`rs_free` itself `beq $s0, $zero` and returns, so a NULL malloc is
a skip, not a Gap. Both functions dereference the asset before the
free, so a NULL return would fault first; that is the same unproven
allocator-failure edge s3604–s3610 left open.

## Remaining functions

### `hangarLoadShadows` (`0x800AE9E0`) — one free

`$a0` is the ROM name at `0x800A5804`. There is one `jr $ra`, at
the function tail. The only interior back-edge is the 14-iteration
image walk (`$s2 < 0xE`); it cannot skip `load_asset` or the free.

`load_asset` then `addu $s4, $v0` is the only assignment of `$s4`
before the epilogue restore. The walk copies `$s4` into `$s1` and
advances `$s1` by packed record sizes (`lw 0($s1)` + 7, `and -4`);
`$s4` is not rewritten. Each record calls
`full_header_image_offset_convert($s1+4, $s1+4)` and
`registerHmtTextureInTable($sp+0x10, $s1+4)`, stores the returned
texture-id halfword at `0x8013A528 + 2*$s2`, then loops. After the
walk, `rs_free($s4)`.

The single generated caller is `mallocCraftSelectionData`
(`0x800AA1A4`). It does not keep `$v0` or `$s4`.

### `loadFontAsset` (`0x80061A88`) — one free, six iterations

Copies a 0x24-byte ROM template from `0x8003B6BC` onto `$sp+0x50`
and `rs_memset($sp+0x78, 0, 0x34)`. `$s5` captures `$sp+0x78` and
`$s6` captures `$sp+0x50` before the loop; those stack headers are
not freed. There is one `jr $ra`, at the function tail. The only
interior back-edge is the 6-iteration glyph walk (`$s2 < 0x6`); it
cannot skip `load_asset` or the free.

Each iteration `sprintf`s a name from `0x8009ED70[$s2]`,
`load_asset`s it, and `addu $s0, $v0`. That is the only assignment
of `$s0` between the pre-loop `$sp+0x78` capture and the epilogue
restore. Header bytes are copied off `$s0`; `sw $s0+0xC, 0x78($sp)`
sets the scratch pixel word to the asset payload; then
`registerHmtTextureInTable($sp+0x50, $sp+0x78)` and a texture-id
halfword is stored at `0x80139980 + 2*$s2`. If the byte argument
is nonzero, the same id is also stored at `0x80139970 + 2*$s2` and
the second register is skipped; otherwise a second register with
the `'S'` name-byte runs and stores that id. Both paths meet at
`L_80061C24` and `rs_free($s0)`. The next iteration overwrites
`$s0` with a new `load_asset` return before the next free.

Generated callers: `mallocCraftSelectionData` (`0x800AAC18`,
`$a0=0`), `initCraftSelectScreen` (`0x800AF0A4`, `$a0=0`), and
`initVwingHudAndSlotState` (`0x800B9430`, `$a0=1`). None keep
`$s0`.

### Helpers — do not free these

`registerHmtTextureInTable` (`0x80022B90`) has no `jal rs_free`.
`full_header_image_offset_convert` (`0x80055488`) has no
`jal rs_free` and no `jal rs_malloc`. `sprintf` and `rs_memset`
likewise do not free the `load_asset` pointer.

## Double-free / non-allocator edges

Hangar `$s4` lives in a callee-saved register for one call. The
next call `load_asset`s again before the next free.

Font `$s0` is rebuilt from a new `load_asset` on every loop
iteration and on every subsequent call. Sequential double-free of
the same register is blocked by rebuild-before-next-free.

Neither pointer has a sibling destructor. Callers consume the
texture-id halfword tables, not the freed assets.

Re-init without shutdown, malloc-size zero, and allocator failure
are the same unproven runtime edges s3604–s3610 left open, not a
second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected: the two
pointers are the hangar `$s4` asset and the per-iter font `$s0`
asset.
