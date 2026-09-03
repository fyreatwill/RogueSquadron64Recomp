# M3 s3615 — remaining model-viewer mesh-chain rs_free

## Work unit

Static census of every generated original `jal rs_free` in
`freeModelViewerMeshChain`. Remaining funcs_37 mesh frees after
the closed `shutdownModelViewer` header-word class: `0x800CBBE8`
of `0x5C($s1)`, `0x800CBBF0` of `$s1`, and `0x800CBC08` of
`0x800D0110`. Classified every original `sw` of each pointer and
whether a free can run on a non-allocator or already-freed
value, including the linked-list walk from `0x10($a0)`
(`runModelViewerLoop` passes `$sp+0x40`). No build or runtime
run was performed.

The discriminator was the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: shutdownModelViewer header-word,
lookup-table, loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`, format-message
`rs_free`, speech-file `rs_free`, speech/cache `rs_free`, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input,
hangar-Y.

## Census size

Original `jal 0x80001C98` in `freeModelViewerMeshChain`: three
sites, all this class. `funcs_37.c` still has later `rs_free` in
`tickMultiPartVoiceLine`, `npcAtAtUpdate`, `npcAtStUpdate`, and
`playerAtStUpdate`.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| vertex/scratch child | `0x5C(node)` | `buildModelViewerTextPage` `sw $zero, 0x5C($s2)` `0x800CA81C`; `sw $a0, 0x5C($s2)` `0x800CA8C4` (`$a0` is the `rs_malloc($s4)` at `0x800CA8A8`, also stored to `0x24($s2)`) | `rs_malloc($s4)` `0x800CA8A8` when `$s1 != 0`; `$s4` starts 0 per node and grows `0x30` per glyph | constructor wrap-retry `0x800CA9B4` of `$a0` then `L_800CA80C` zeros `0x5C`; destructor `0x800CBBE8` skips NULL |
| mesh/text node | `$s1` | `appendNodeToListHead` stores `$s2` at `0x10($a0)` or `0x0(tail)` | `rs_malloc(0x60)` `0x800CA800`; memset `0x5C` bytes zeros `0x0`/`0x4` | `0x800CBBF0` of `$s1`; walk copies next from `0x0` first |
| text-page table | `0x800D0110` | `buildModelViewerTextPage` delay-slot `sw $v0, 0x110($v1)` `0x800CA7EC`; `$v1=0x800D` | `rs_malloc(count*56)` `0x800CA7C4` (`((n&0xFFFF)*7)<<3`) | `0x800CBC08` of `$a0`; no skip, no post-free NULL |

Those are the only original stores of those three values as
heap pointers. `rs_free` itself `beq $s0, $zero` and returns, so
a NULL `0x5C` or a NULL `0x800D0110` is a skip, not a Gap.
`0x24(node)` aliases `0x5C`; the destructor frees only `0x5C`.

## Remaining function

### `freeModelViewerMeshChain` (`0x800CBBB8`) — three frees

Frame is `-0x20`. `$a0` is the list object. Order:

1. `lw $s0, 0x10($a0)`. If NULL, skip the walk (`L_800CBC04`).
2. `$s1 = $s0`. Loop:
   - `lw $a0, 0x5C($s1)`; `lw $s0, 0x0($s0)` (next, before free).
   - If `0x5C` non-NULL, `jal rs_free` at `0x800CBBE8`.
   - `jal rs_free` at `0x800CBBF0` with delay-slot
     `addu $a0, $s1, $zero` (the node).
   - If next non-NULL, `$s1 = $s0` and repeat.
3. `lui $v0, 0x800D`; `lw $a0, 0x110($v0)`; `jal rs_free` at
   `0x800CBC08`.
4. One `jr $ra`.

No generated path reaches the return without the table free.
None of the three words is NULLed by this function. The walk
does not load `0x20(node)`.

## Matching init

### `buildModelViewerTextPage` (`0x800CA714`) — only writer

The only generated `jal 0x800CA714` is `runModelViewerLoop`
`0x800C9D60` with `$a0=$s0` (craft index) and `$a1=$s7`.
`$s7` is `$sp+0x40` (`addiu $a2, 0x40; addu $v0, $sp, $a2;
addu $s7, $v0`). That is the same object later passed to the
destructor (`0x800CA5D4 addiu $a0, $sp, 0x40`).

`rs_memset($a1, 0, 0x4C)` at `0x800CA7E8` zeros `0x10` of that
object (the list head) in the delay slot of
`sw $v0, 0x110($v1)` after the table malloc.

Per line, `rs_malloc(0x60)` at `0x800CA800` produces `$s2`.
`L_800CA80C` memsets `0x5C` bytes and `sw $zero, 0x5C($s2)`.
When the line has glyphs (`$s1 != 0`), `rs_malloc($s4)` at
`0x800CA8A8` is stored to both `0x24($s2)` and `0x5C($s2)`,
then `zmemcpy` into that buffer. `appendNodeToListHead`
(`0x800CAAC4`) links `$s2` onto `0x10($a1)`. If more
characters remain, the loop mallocs another `0x60` node
(`bne $s5, L_800CA800`).

`$s7` (glyph index) indexes 56-byte records in `0x800D0110`.
`appendNodeToListTail($s2, table+$s7*56)` at `0x800CAD0C`
hangs those interior records on `0x20(node)`. The destructor
does not free `0x20` entries; the parent table free covers
them.

### Wrap-retry inner free — not a sibling destructor gap

If `0x1820($sp)==0` (the `'*'` / wrap flag is clear) and the
computed spacing compare `c.lt.s $f2, $f4` holds, `0x800CA9B4`
`jal rs_free` with `$a0` still `0x5C($s2)` from `0x800CA900`.
The delay slot only rewinds `$s3`. The function then jumps to
`L_800CA80C`, which memsets the same `0x60` node and
`sw $zero, 0x5C($s2)`. `$s1` and `$s4` are reset to 0. The
node has not yet been appended. The shutdown free therefore
sees either NULL or a later matching `rs_malloc($s4)`, not the
already-freed wrap-retry pointer.

The only jump to `L_800CA980` is that `0x1820==0` branch; the
only jump to `L_800CA80C` after construction is this retry.

## Consumers — do not free these words

`appendNodeToListHead` (`0x800CBDC4`) is the only generated
caller of the `0x10` list writer besides the initial memset.
The only generated `jal 0x800CBDC4` is `0x800CAAC4`.
`appendNodeToListTail` writes `0x20(node)`, not `0x10` of the
`$sp+0x40` object.

`releaseMeshLinkedList` (`0x800CBB7C`) is the only other
walker of `0x10($a0)`. The only generated `jal 0x800CBB7C` is
`runModelViewerLoop` `0x800CA0F0` with `$a0=$sp+0x40`. It
calls `enqueueMeshForDeferredRelease` on each node. That
helper copies GPU fields `0x3C..0x58` into a slot when
`0xC(node) & 0x10` is set, then clears that bit. It has no
`jal rs_free` and does not unlink the CPU list.

Loads of `0x800D0110` besides the destructor are
`0x800CABE4` and `0x800CAD04` (table-base plus `$s7*56` for
GBI setup / tail-append). No other original
`sw $v0, 0x110($v1)` uses `lui 0x800D`.

No generated `jal rs_free` loads `0x24(node)`.

## Pairing / double-free

The only generated `jal 0x800CBBB8` is `runModelViewerLoop`
`0x800CA5D0`, on the epilogue path after
`releaseModelViewerModelAssets` and before
`shutdownModelViewer`, then `jr $ra` at `0x800CA630`. The
only generated `jal 0x800CA714` is the matching init above.
No `lui`/`ori`/`addiu` constructs either address.

Sequential double-free of the nodes / `0x5C` / `0x800D0110`
is blocked by that single build/free pair. The wrap-retry
inner free NULLs `0x5C` before reuse. Sequential double-free
through `0x24` is blocked by the missing `0x24` free. Re-init
without shutdown would leak the previous table and list;
a first-malloc failure stores NULL and `rs_free` skips.
Those are the same unproven re-init / allocator edges
s3604–s3614 left open, not a second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope. `H-NextClassUnevaluable` is not
selected: the three pointers are the `0x60` nodes, their
`$s4` vertex/scratch child (or NULL), and the `count*56`
text-page table.
