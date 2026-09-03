# M3 s3613 — remaining lookup-table rs_free

## Work unit

Static census of every generated original `jal rs_free` in
`rebuildActiveDisplayObjectList` and `destroyLookupTable`. Remaining
funcs_14 lookup-table frees after the closed loadCharTextureSet
DMA-array class: the one `rebuildActiveDisplayObjectList` free
(`0x800645AC` of the local scratch `$a0`) and the two
`destroyLookupTable` frees (`0x8006463C` of `0x0($s0)`,
`0x80064644` of `$s0`). Classified every original `sw` of each
pointer and whether a free can run on a non-allocator or
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

Closed classes were not repeated: loadCharTextureSet DMA-array,
load_asset-then-free, texture-scratch `rs_free`, text-texture
`rs_free`, format-message `rs_free`, speech-file `rs_free`,
speech/cache `rs_free`, destructor skipped-NULL, destructor
unchecked-free, `-0x6904` alias, remaining-indexer, `-0x6908`
non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_14.c`: six sites. Three are
this class. The other three (`loadCharTextureSet`, `loadFontAsset`,
`buildPlayerCraftAssetTemplate`) are already-closed classes. After
this census, funcs_14 has no remaining `rs_free`.

The planned-unit phrase "of `0x0($a0)`" for the rebuild site is a
misread of `lw $s0, 0x0($a0)` immediately before the `jal`. The
delay slot is `nop`, so `rs_free` receives `$a0` itself.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| rebuild scratch | `$a0` after `0x800644AC` | `rs_malloc` `0x800644A0`; `sw $zero, 0($a0)` `0x800644B0`; kept-object `sw $s0` into scratch words `0x80064524` | `rs_malloc(0x400, 0)` | `0x800645AC` of `$a0`; no skip, no post-free NULL |
| lookup header | allocateSlotTable `$s1` | `rs_malloc(8, 0)` `0x800645E4` | that malloc | `destroyLookupTable` `0x80064644` of `$s0`; no generated caller |
| lookup slots | `0x0(header)` | `sw $v0, 0($s1)` `0x80064604` | `rs_malloc(count<<3, 0)` `0x800645FC` | `destroyLookupTable` `0x8006463C` of `0x0($s0)`; no generated caller |

`rs_free` itself `beq $s0, $zero` and returns, so a NULL slots
word is a skip, not a Gap. A NULL header would `lw 0($s0)` before
the first `jal` and is crash-before-free.

## Remaining functions

### `rebuildActiveDisplayObjectList` (`0x80064488`) — one free

Frame is `-0x20`. `$s1` captures incoming `$a0` (a lookup header).
The only `jal`s are `rs_malloc` then `rs_free`. `$a0` is set to
the malloc return at `0x800644AC` and is never rewritten.

`sw $zero, 0($a0)` zeros scratch word 0. `lhu 0x4($s1)` is the
used count. If it is 0, or if the keep-count `$a1` stays 0, the
relink walk is skipped. Otherwise the function walks
`0x0($s1)` as an 8-byte slot array, copies live object pointers
into scratch, then rewrites each object's `+0`/`+4` as a
doubly-linked list. `lw $s0, 0($a0)` at `0x800645A8` is that
list head (or 0) and is the return value. `jal rs_free` at
`0x800645AC` then frees the scratch. There is one `jr $ra`, and
no generated path reaches it without the free.

Callers pass a lookup-header global as `$a0`. None keep the
scratch. Generated `jal 0x80064488` sites: `slotEffectHandlerDispatch`,
`runHangarSelectionFrame`, `tickCraftSelectScreen`,
`menuControllerInput`, `runMenuRandomBackdropScreen`,
`runMenuShipSelectScreen`, `runMenuModelViewerScreen`,
`menuSubtype02Handler`, `runModelViewerLoop`.

A NULL malloc would `sw $zero, 0($a0)` before the free:
crash-before-free, the same unproven allocator-failure edge
s3604–s3612 left open. The keep-index is `andi 0xFF` into a
0x400-byte (256-word) scratch; an `lhu 0x4($s1) > 256` used
count would spin on the byte-masked walk, not free a second
pointer.

### `allocateSlotTable` (`0x800645CC`) — matching init

`$s0` is the capacity argument. `rs_malloc(8)` is the header;
the delay slot of the second `jal` captures it in `$s1`.
`rs_malloc(count<<3)` is the slot array, stored at `0x0($s1)`.
`$v0` is then rebound to the header; `sh $zero, 4($v0)` and
`sh $s0, 6($v0)` write used/capacity. That `sw $v0, 0($s1)` at
`0x80064604` is the only generated store of the slots word.

Generated callers and header stores:

| Caller | Capacity | Header store |
|---|---|---|
| `mallocCraftSelectionData` | 8 | `0x800CD668` (`sw $v0, -0x2998` / `lui 0x800D`) |
| `initSceneForMission` | 4, 4 | `0x800B0AFC`, `0x800B0B00` |
| `initCraftSelectScreen` | 0x40 | `0x800CDCDC` (`-0x2324`) |
| `initVwingHudAndSlotState` | 0x40, 8, 8 | `0x800CF078`, `0x800CF07C`, `0x800CF080` (`-0xF88/-0xF84/-0xF80`) |
| `initMenuScreenRenderContext` | 0x40, 8 | `0x800CF078`, `0x800CF07C` |
| `initMenuScreenCameraViewport` | 0x10 | `0x800CF078` |
| `initInteractiveSceneContext` | 0x10, 0x10 | `0x800CF078`, `0x800CF07C` |
| `initModelViewer` | 8, 8 | `0x800D0360`, `0x800D0364` |

Those `sw $v0` (and the camera-viewport `sw $a0` of the already-captured
return) are the only original stores of those header words.

### `destroyLookupTable` (`0x80064628`) — two frees

`$s0` captures incoming `$a0`. `lw $a0, 0($s0)` then `jal rs_free`
releases the slots word. The second `jal` delay slot is
`addu $a0, $s0, $zero`, so the header itself is freed next.
Neither free NULLs. `$s0` is callee-saved across the first
`jal`. There is one `jr $ra`.

No generated `jal 0x80064628` exists. The address is not built
by `lui`/`ori`/`addiu` anywhere in `RecompiledFuncs`. The only
other `lw $a0, 0x0($reg); jal rs_free` sites are
`funcs_11.c` `0x80054AC4` and `funcs_13.c` `0x8005B35C`, which
are different objects.

### Helpers — do not free these

`findLookupEntryByKey` (`0x800642A0`) and
`removeLookupTableEntry` (`0x800643C4`) load `0x0(header)` as
the slot array and write 8-byte records inside it. They
`sh` the used halfword at `+4`. They do not rewrite the slots
pointer and have no `jal rs_free`. `getLookupEntryField5`,
`setLookupEntryField5ByKey`, and `relocateLookupEntryToNewKey`
likewise have no `jal rs_free`.

## Double-free / non-allocator edges

Rebuild scratch is callee-local: one malloc, one free, no store
to a global. The next call mallocs a new 0x400 buffer.

Sequential double-free of a lookup header or slots word through
`destroyLookupTable` is blocked by the missing caller.

`shutdownModelViewer` (`0x800CBB30`) `lw`/`jal rs_free` of
`0x800D0364` then `0x800D0360` frees those headers without
calling `destroyLookupTable` and without freeing `0x0(header)`.
That is a later class. It cannot double-free with this destructor
because this destructor never runs.

Re-init of a header global without shutdown leaks the previous
table. A first-malloc failure would `sw` through a NULL header
before return. Those are the same unproven re-init / allocator
edges s3604–s3612 left open, not a second pointer source for
these three frees.

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted
at static scope. `H-NextClassUnevaluable` is not selected: the
three pointers are the rebuild scratch and the
`allocateSlotTable` header/slots pair.
