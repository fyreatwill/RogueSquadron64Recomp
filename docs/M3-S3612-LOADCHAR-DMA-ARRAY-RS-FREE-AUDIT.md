# M3 s3612 — remaining loadCharTextureSet rs_free

## Work unit

Static census of every generated original `jal rs_free` in
`loadCharTextureSet`. Remaining scratch DMA-array free after the
closed load_asset-then-free class: the one `loadCharTextureSet`
free (`0x80061910` of `0x0($s0)` walking the 8-slot stack array
at `$sp+0xB8`). Classified every original `sw` of each pointer
and whether a free can run on a non-allocator or already-freed
value. No build or runtime run was performed.

The discriminator was the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`, format-message
`rs_free`, speech-file `rs_free`, speech/cache `rs_free`,
destructor skipped-NULL, destructor unchecked-free, `-0x6904`
alias, remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input,
hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_14.c`: six sites. One is this
class. The other five (`loadFontAsset`, `buildPlayerCraftAssetTemplate`,
`rebuildActiveDisplayObjectList`, and `destroyLookupTable` ×2) are
already-closed or later classes.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| font mipmap DMA slot `i` | `$sp+0xB8+4*i`, `i<8` | zero-init `sw $zero` `0x80061560`; DMA `sw $v0` `0x80061604`; post-free `sw $zero` `0x80061918` | `rs_malloc` `0x800615E0` of `get_asset_size_extra` | `0x80061910` then NULL; NULL slots skip |

`$s4` is `lw` from the word table at `0x8009FC10` indexed by
argument `$a1`. `$s0` at entry is the same table indexed by the
low byte of `$a1`. Generated callers pass `$a1` in `{0,2,5,6,8,9,0xB}`
or a halfword loaded from `0x80139014`; those values are `<256`, so
the two loads alias on the generated call sites. The 8-slot array
is callee stack, not a field of `$s4`.

`rs_free` itself `beq $s0, $zero` and returns, so a NULL malloc is
a skip, not a Gap. The free loop also `beq $a0, $zero` before the
`jal`.

## Remaining function

### `loadCharTextureSet` (`0x800613C0`) — one free, 8 slots

Frame is `-0x120`. There is one `jr $ra`, at the function tail.
The 8-word array is zeroed before any DMA:

```
addiu $v1, $sp, 0xB8          # 0x80061558
sw    $zero, 0x0($v1)         # 0x80061560, 8 iters, $v1 += 4
```

`$s2` is `0` entering that loop (`addu $s2, $a1, $zero` at
`0x80061538` with `$a1=0`). The two `rs_malloc` calls immediately
before it store into `$s4+0x28` and `$s4+0x24`, not into the array.

If `lbu 0x1D($s4)==0`, the DMA loop is skipped (`beq` to
`L_8006165C`) and every slot stays zero. Otherwise `$s2` is reset
to 0 and each iteration:

1. `sprintf`s a suffix `_mm%ld` into `$sp+0xD8` when `$s2!=0`
   (skipped on slot 0).
2. `sprintf`s `fonts/%s%s` into `$sp+0x18` from `$s4+0x10` and
   that suffix.
3. `$s3 = get_asset_size_extra(-1, $sp+0x18)`. `-1` or `0` leaves
   remaining slots zero and jumps to `L_8006165C`.
4. `rs_malloc($s3, 0)`; `$s0 = $sp+0xB8 + ($s2<<2)`; `sw $v0, 0($s0)`.
   That is the only non-zero store into the 8 words.
5. `findAssetAcrossSegments` / `setupAssetDma` (dest = that word)
   / `teardownAssetDma`.
6. `$s2++`; `sb $s2, 0xE6($sp)`; loop while `$s2 < lbu 0x1D($s4)`.

After the glyph walk (or the `lhu 0($s4)==0` skip to
`L_800618FC`), the free loop always runs 8 times:

```
addiu $s0, $sp, 0xB8          # 0x80061900
lw    $a0, 0x0($s0)
beq   $a0, $zero, L_8006191C
jal   rs_free                 # 0x80061910
sw    $zero, 0x0($s0)         # 0x80061918
sltiu $v0, $s2, 0x8
```

No generated path reaches the epilogue without this walk. The
glyph walk writes interior pointers `slot + computed + 0xC` into
the parallel `$sp+0x80` array and passes `$sp+0x80` to
`registerHmtTextureInTable`; those interiors are not freed. The
walk ends before the free loop, and the stack dies on return.

`$s0` is overwritten as a width counter during the glyph walk and
reloaded as `$sp+0xB8` at `0x80061900` before the free. After the
free, `$s0` becomes `$s4` for a separate `0x34($s4)` malloc walk.
That later walk is not this class.

### Helpers — do not free these

`get_asset_size_extra` (`0x80004D5C`), `findAssetAcrossSegments`
(`0x80004AAC`), `setupAssetDma` (`0x80004E70`), `teardownAssetDma`
(`0x80004C70`), `zmemcpy` (`0x80018EF4`), and
`registerHmtTextureInTable` (`0x80022B90`) have no `jal rs_free`
and no `jal rs_malloc`. `sprintf` jals `0x80035FD0` only.

Persistent object mallocs stored on `$s4`/`$s0` (`+0x20` 0x100-byte
remap, `+0x24`, `+0x28`, `+0x34` slices, `+0xEC`, `+0xF0`) are
returned live and are outside this class.

### Callers — do not keep the array

Generated callers: `initVoiceSubtitleSystem` (`0x80055B08`),
`mallocCraftSelectionData` (`0x800AAC30`, `0x800AAC44`),
`initCraftSelectScreen` (`0x800AF0BC`, `0x800AF0D0`, `0x800AF0E4`),
`initVwingHudAndSlotState` (`0x800B9444`, `0x800B9458`, `0x800B946C`),
`initMenuScreenCameraViewport` (`0x800C2ED8`),
`initInteractiveSceneContext` (`0x800C40A8`),
`createMenuTextElement` (`0x800C5350`),
`initModelViewer` (`0x800CA6E8`). None keep `$sp+0xB8`.

## Double-free / non-allocator edges

Each of the 8 words is only ever 0 or the matching `rs_malloc`
return from that iteration. Sequential double-free of a slot is
blocked by the post-free NULL and by the free loop running once
per call. The next call zero-inits the new frame before any DMA.

The DMA bound `lbu 0x1D($s4)` is a byte and is not stored in this
function. If it were `>8`, extra `sw $v0` would land past
`$sp+0xD4`, outside the 8-word free walk — a leak/overflow, not a
free of a non-allocator slot. The 8 freed words would still be 0
or malloc. No generated `sb ..., 0x1D($s4)` exists; the bound is
unproven and is not a second pointer source for this class.

If DMA is skipped or the first `get_asset_size_extra` fails while
`lhu 0($s4)!=0`, `L_8006165C` does `lw $v1, 0xB8($sp)` then
`lbu 0x8($v1)` on a NULL slot. That is a crash-before-free, not a
Gap. If `lhu 0($s4)==0`, that load is skipped and the free loop
skips zeros.

Re-init without shutdown, malloc-size zero, and allocator failure
are the same unproven runtime edges s3604–s3611 left open, not a
second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected: every
freed word is a slot of the same 8-word stack array.
