# M3 s3650 — destroyTextureLUTs rs_free of *0x80128F08 / *0x80128EFC

## Work unit

Static census of `destroyTextureLUTs` `jal rs_free`
at `0x8001E344` (`$a0` = `*0x80128F08`) and
the sibling `jal rs_free` at `0x8001E354`
(`$a0` = `*0x80128EFC`). Enumerated every
original load/store of those two words
(including the matching allocator stores,
every later store, and whether any caller
holds the buffers) and every `jal rs_free`
that can receive those pointers. Other loads
were classified as consumers or as a second
free. No build or runtime run was performed.

The two words are gp-relative from `0x80130000`:
`-0x70F8` = `0x80128F08` (0x24-stride LUT
table) and `-0x7104` = `0x80128EFC`
(word-stride pointer array). Absolute
`0x80128F08` / `0x80128EFC` never appear in
generated code.

The discriminator was the single complete
original census of those two `jal rs_free`
sites plus every original `lw`/`sw` of
`*0x80128F08` and `*0x80128EFC` that can
become this `$a0`, and every `jal rs_free`
that can receive those pointers. No overlay
duplicate of `destroyTextureLUTs` /
`0x8001E334` exists as a second generated
body.

- H-NextClassGap: a remaining free can pass a
  pointer that is not the matching allocator
  store, or can free it after a sibling already
  released it without a NULL.
- H-NextClassComplete: every remaining free is
  a destructor of a matching init store, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object
  identities or unshared writers prevent a
  complete classification of a pointer source.

Closed classes were not repeated. Host
`TEXDATA_TABLE_GUARD` / `TEXDATA_PTR_ARRAY_GUARD`
substitutions at these two loads (s468/s470)
are not original skips. Do not land a
skip-path NULL store for the s3636 overlay
Gap unless this census identifies that same
writer as this word.

## Census size

Original `jal 0x80001C98` in `funcs_6.c`: 3
sites. Two are this class (`0x8001E344`,
`0x8001E354`). The remaining site is
`uploadTextureDescriptorData` `0x800232CC`
(`$a0` = `$s1` = incoming `$a1`), a different
object.

`destroyTextureLUTs` is `0x8001E334`..
`0x8001E36C`, frame `-0x18`. One generated
`jal 0x8001E334` (`freeRenderSubsystemResources`
`0x80018658`). Zero `LOOKUP_FUNC(0x8001E334)`.
Zero `lui`/`addiu` function-pointer
constructions of `0x8001E334`. One
overlay-table entry (rom offset `0x1DEF4`,
size `0x38`); not a second generated body.
Single `jr $ra` at `0x8001E364`.
`packTlutEntriesRgba5551` starts at
`0x8001E36C` immediately after. Zero
`static_*` clones of these PCs.

`freeRenderSubsystemResources` itself has
zero generated `jal 0x80018650`, zero
`LOOKUP_FUNC(0x80018650)`, and zero
`lui`/`addiu` constructions. One
overlay-table entry (rom offset `0x18210`,
size `0x88`); not a second generated body.
The destructor wrapper is original code
reachable only through that overlay mapping.

There is no original NULL skip and no
post-free NULL. After a live malloc store,
the destructor is straight-line: load
`*0x80128F08`, `jal rs_free`, load
`*0x80128EFC`, `jal rs_free`, return. Host
TEXDATA substitutions at `0x8001E338` /
`0x8001E350` replace an OOB loaded value
with `0x80000000` and still call `rs_free`;
that is not an original skip.

## `*0x80128F08` / `*0x80128EFC` accesses

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| LUT malloc | `0x8001E25C`/`0x8001E274` | `jal rs_malloc((a0&0xFFFF)*0x24, 0)`; `sw $v0, -0x70F8` | `*0x80128F08` | live heap-pointer writer |
| ptr-array malloc | `0x8001E278`/`0x8001E290` | `jal rs_malloc((*0x80128F04)<<2, 0)`; `sw $v0, -0x7104` | `*0x80128EFC` | live heap-pointer writer |
| LUT zero-fill | `0x8001E2BC` | `lw -0x70F8`; `sh $zero, 0x0` stride `0x24` | `*0x80128F08` | consumer of the just-stored table |
| ptr-array zero-fill | `0x8001E2EC` | `lw -0x7104`; `sw $zero, 0x0` stride `4` | `*0x80128EFC` | consumer of the just-stored array |
| clone LUT malloc | `0x80022878`/`0x80022890` | same formula from saved counts | `*0x80128F08` | unreferenced second store |
| clone ptr-array malloc | `0x80022894`/`0x800228AC` | same formula from saved counts | `*0x80128EFC` | unreferenced second store |
| clone zero-fills | `0x800228D8`/`0x80022908` | same walks | both | unreferenced consumers |
| LUT destructor | `0x8001E338`/`0x8001E344` | `lw -0x70F8`; `jal rs_free` | `*0x80128F08` | destructor; no NULL skip; no post-free NULL |
| ptr-array destructor | `0x8001E350`/`0x8001E354` | `lw -0x7104`; `jal rs_free` | `*0x80128EFC` | destructor; no NULL skip; no post-free NULL |

`0x80128F04` above is `-0x70FC` from
`0x80130000` (the saved `$a1` count
halfword), not this class.

64 original `lw`/`sw` of `-0x70F8`/`-0x7104`
exist in `funcs_*.c`. All 0x8013-base sites
are in `funcs_6.c`. `funcs_42.c` `lwc1`
`-0x7104`/`-0x70F8` use `$at = 0x800B`
(`0x800A8EFC` / `0x800A8F08`), not these
words.

## Object identity

### Live allocator — `initTextureLUTAndAllocBuffers`

`initTextureLUTAndAllocBuffers` is
`0x8001E230`..`0x8001E334`, frame `-0x28`.
One generated `jal 0x8001E230`
(`buildAndRegisterDefaultMaterial`
`0x80018004` with `$a0 = $a1 = $s4 & 0xFFFF`).
Zero `LOOKUP_FUNC(0x8001E230)`. Zero
`lui`/`addiu` constructions. One
overlay-table entry (rom offset `0x1DDF0`,
size `0x104`); not a second generated body.

Sequence:

1. Store `$a1` at `*0x80128F04` (`-0x70FC`)
   and `$a0` at `*0x80128EF0` (`-0x7110`).
2. `rs_malloc((a0&0xFFFF)*0x24, 0)` into
   `*0x80128F08`. Flags `0` is not flags-4
   and not flags-8. No original NULL check.
3. `rs_malloc((*0x80128F04)<<2, 0)` into
   `*0x80128EFC`.
4. `rs_malloc((*0x80128EF0)<<2, 0)` into
   `*0x80128F00` (`-0x7100`). That sibling
   is not this class: `destroyTextureLUTs`
   does not load or free it, and no
   `jal rs_free` in `funcs_6.c` receives it.
5. If the LUT count is `> 0`, walk
   `*0x80128F08` with stride `0x24` and
   `sh $zero, 0x0`. If the pointer-array
   count is `> 0`, walk `*0x80128EFC` with
   stride `4` and `sw $zero, 0x0`.

The only live original heap-pointer writers
of these two words are the flags-0 malloc
stores at `0x8001E274` and `0x8001E290`.

`buildAndRegisterDefaultMaterial`
(`0x80017B88`, size `0x604`) does not return
or keep those pointers. Two generated callers
invoke it, so the live init can run more than
once:

| Caller | PC | Gate before the jal |
|---|---|---|
| `advanceVideoFrame` | `0x800183F8` | none; the `beq $v0, 0` at `0x80018404` is after the return |
| `initVideoBootWrapper` | `0x800185DC` | none; the `beq $v0, 0` at `0x800185E8` is after the return |

A second init overwrites the globals without
freeing the previous pair. That is a leak of
the first mallocs, not a second free. The
destructor still receives the latest matching
allocator store. Neither caller holds the
buffers across the call.

### Unreferenced clone — `initTextureMaterialPools`

`initTextureMaterialPools` (`0x80022844`,
size `0x154`) is a near-clone: it reloads the
saved counts, mallocs the same three buffers
with flags `0`, stores them over the same
globals, and repeats the zero-fill walks.
Zero generated `jal 0x80022844`. Zero
`LOOKUP_FUNC(0x80022844)`. Zero `lui`/`addiu`
constructions. One overlay-table entry (rom
offset `0x22404`, size `0x154`); the same
generated body, not a second body. Those
stores cannot fire through a generated call,
overlay lookup, or function-pointer
construction.

### Consumers — table-base reloads, not a second free

54 remaining 0x8013-base loads (18 functions)
use the globals as a table base. None of
those functions contains a `jal 0x80001C98`.
`freeTextureDataSlot` is the most free-shaped
name: each of its four `-0x70F8` loads is
followed by `index * 0x24` arithmetic and
field reads at `+0x0`/`+0xC`/`+0x10`; it
calls `unlinkTextureMaterialList` with the
slot index, not the table pointer, and does
not `jal rs_free`. `allocTextureTlutBlock`
and `freeTextureTlutBlock` walk
`*0x80128EFC` as `index * 4` slots. The
other 15 functions (`loadTextureToMemory`,
`loadTextureTile`, `loadAndDecodeTexture`,
`emitMaterialRenderStateDL`,
`getTextureLUTFieldAt8`/`AtA`,
`getTextureDimsBySlot`,
`findMatchingTextureRecursive`,
`findTextureByName`,
`copyTextureDescriptorWithData`,
`fillTextureDescriptorNoCopy`,
`getTextureDataByMaterialId`,
`getTextureTlutEntry`,
`getTextureAttrBySlot`,
`texPackTlutSlotOrAlloc`,
`texPackTlutAtIndex`,
`unpackTlutToRgbaBytes`,
`shiftTlutEntryWithinChunk`) are the same
index-into-table shape.

`uploadTextureDescriptorData` `$s1` at
`0x800232CC` is incoming `$a1` (caller
`tickWrappingTimerAccumulatorList`
`0x8005477C` computes `$a1` as an interior
of `0x0($s2)`), not these globals.

### Caller-side stores

`destroyTextureLUTs` does not publish `$v0`.
`freeRenderSubsystemResources` next frees
`*0x8012A444` (`-0x5BBC` from `0x8012`), a
different global, then four more `rs_free`
sites of that wrapper's own objects. It does
not reload `*0x80128F08` / `*0x80128EFC`.

This pair is not the s3636 overlay `0x1C` /
`0x20` writer.

Failed malloc (`$v0 == 0`) still stores NULL
and a later destructor call reaches
`rs_free`, which skips. The zero-fill walks
and every consumer would dereference first.
That is the same unproven allocator-failure
edge s3604–s3648 left open.

## Pairing

One generated destructor of both words. The
unreferenced clone cannot fire. There is no
second `jal rs_free` of either pointer.
Sequential double-free of the dangling
post-free global would require a second call
of `destroyTextureLUTs`; the only generated
caller is `freeRenderSubsystemResources`,
which itself has no generated caller. Same
unchecked-NULL destructor shape already
closed as Complete for earlier classes.
Runtime allocator legitimacy and whether
every call's malloc succeeds remain
unproven. Re-init without an intervening
destroy leaks the previous pair; it does not
feed a non-allocator pointer to the free.

## Classification

The only `jal rs_free` sites that can receive
these pointers are `0x8001E344` and
`0x8001E354`. The only live original
heap-pointer writers are the flags-0 malloc
stores at `0x8001E274` and `0x8001E290`.
`initTextureMaterialPools` is an unreferenced
clone of that same formula, not a second
object identity. All other loads are
table-base consumers. Host TEXDATA
substitutions are not original skips.
This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected:
one 0x24-stride LUT-table identity and one
word-stride pointer-array identity, each
with one live allocator store.

No guard was added. Runtime allocator state
remains unproven. The s3636 overlay skip-path
NULL store was not landed: these words are
not that writer.

## Next remaining `jal rs_free`

The next remaining original site in
`funcs_6.c` is `uploadTextureDescriptorData`
`0x800232CC` (`$a0` = `$s1` = incoming `$a1`).
That is the last remaining original
`jal 0x80001C98` in `funcs_6.c`.
