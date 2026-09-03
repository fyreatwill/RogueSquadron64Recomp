# M3 s3651 — uploadTextureDescriptorData rs_free of $s1

## Work unit

Static census of `uploadTextureDescriptorData` `jal rs_free`
at `0x800232CC` (`$a0` = `$s1`, bound at
`0x800232A8` to incoming `$a1`). Enumerated
every original load/store of that `$s1`
(including the matching allocator if any,
every later store, whether the caller
`tickWrappingTimerAccumulatorList`
`0x8005477C` holds the buffer, and the
interior `$a1 = 0x0($s2) + (*(*s2+0xC) *
($s1&0xFFFF) + 0x14)` delay-slot address)
and every `jal rs_free` that can receive
that pointer. Other loads were classified
as consumers or as a second free. No build
or runtime run was performed.

The discriminator was the single complete
original census of that `jal rs_free` site
plus every original `lw`/`sw`/`addu` of
`uploadTextureDescriptorData` `$s1` that
can become this `$a0`, and every
`jal rs_free` that can receive that
pointer. No overlay duplicate of
`uploadTextureDescriptorData` /
`0x80023274` exists as a second generated
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

Closed classes were not repeated. Do not land
a skip-path NULL store for the s3636 overlay
Gap unless this census identifies that same
writer as this `$s1`. Host
`MATERIAL_ARRAY_PTR_GUARD` at `0x80023290`
is not an original skip of this free.

## Census size

Original `jal 0x80001C98` in `funcs_6.c`: 3
sites. Two are `destroyTextureLUTs`
`0x8001E344` / `0x8001E354` (closed s3650).
This is the remaining site.

`uploadTextureDescriptorData` is
`0x80023274`..`0x800232F4`, frame `-0x20`.
One generated `jal 0x80023274`
(`tickWrappingTimerAccumulatorList`
`0x8005477C`). Zero `LOOKUP_FUNC(0x80023274)`.
Zero `lui`/`addiu` function-pointer
constructions of `0x80023274`. One
overlay-table entry (rom offset `0x22E34`,
size `0x84`); not a second generated body.
Single `jr $ra` at `0x800232F0`.
`getTextureDataByMaterialId` starts at
`0x800232F8` immediately after. Zero
`static_*` clones of these PCs.

`tickWrappingTimerAccumulatorList` is
`0x80054650`..`0x800547BC`, overlay size
`0x170`. Three generated callers
(`cinematicLoopBody` `0x800A63F8`,
`runHangarSelectionFrame` `0x800AAF60`,
`runInMissionFrame` `0x800FACB0`). Zero
`LOOKUP_FUNC(0x80054650)`. Zero `lui`/`addiu`
constructions. One overlay-table entry
(rom offset `0x54210`, size `0x170`); not a
second generated body.

## `$s1` accesses

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x80023284` | `sw $s1, 0x14($sp)` | callee-save | not a heap store |
| bind | `0x800232A8` | `addu $s1, $a1` | `$s1` | incoming `$a1`; delay slot of the material-bit0 `beq` |
| memcpy src | `0x800232B4` | `jal memcpy`; `$a1` still `$s1` | `$s1` | consumer; dest is `0x10($s0)` |
| free | `0x800232CC`/`0x800232D0` | `jal rs_free`; `addu $a0, $s1` | `$s1` | gated by `lbu 0x2($s0) & 1`; no post-free NULL |
| epilogue | `0x800232E4` | `lw $s1, 0x14($sp)` | callee-save | restores caller `$s1` |

`$s1` is never stored to a global.

Original skips, both taken on the live path:

1. Material-array `lhu 0x0(idx*4)` bit 0 == 0
   (`0x800232A4`) skips memcpy and free;
   returns 0. Host `MATERIAL_ARRAY_PTR_GUARD`
   at `0x80023290` substitutes an OOB
   `*0x8011A444` (`lui 0x8012; lw -0x5BBC`)
   with `0x80000000`; that is not an original
   skip of this free.
2. `lbu 0x2($s0)` bit 0 == 0 (`0x800232C4`)
   skips free only; returns 1.

## Object identity

### Incoming `$a1` — interior of slot `+0x0`

The only generated caller computes `$a1` in
the delay slot of `jal 0x80023274`:

```
lw   $a0, 0x0($s2)          # converted-buffer header
lw   $v1, 0xC($a0)          # stride
andi $v0, $s1, 0xFFFF       # wrapping remainder (not the buffer)
mult $v1, $v0
mflo $v1
addiu $a1, $v1, 0x14
jal  0x80023274
addu $a1, $a0, $a1          # header + stride*index + 0x14
```

`$s2` walks `*0x80137C84` with stride `0x10`
(the animation-phase pool closed s3634).
`0x0($s2)` is slot `+0x0`. The caller's `$s1`
at this point is `srl` of the slot
accumulator, then the unsigned-div remainder;
it is not a heap pointer.

The interior is never the malloc return:
`+0x14` is the 0x14-byte header size, the
stride at `+0xC` is a zero-extended LUT
halfword (non-negative), and the index is
`andi 0xFFFF` of that remainder. Minimum
offset is `0x14`.

`tickWrappingTimerAccumulatorList` writes
`+0x10` of the header (`getTextureDataByMaterialId`
return, memcpy dest) and slot `+0x8`
(accumulator). It does not store `$a1`. The
caller holds the header at slot `+0x0`, not
the interior. Three outer callers invoke the
tick; none receive this `$s1`.

### Matching allocator of the header, not of `$s1`

The only original heap-pointer writer of
slot `+0x0` is `loadAssetIntoNewSlot`
`0x80054970`: `rs_malloc(frameCount *
stride + 0x14, 0)`, flags 0. `zmemcpy`
copies a 0x14-byte stack header onto that
block. Per-frame `loadAndDecodeTexture`
copies pixels into `header + 0x14 +
n*stride` (the same interior formula). The
DMA scratch `$s6` is a different malloc,
freed at `0x800549E4` (closed s3635).

The matching destructor of the header is
`freeAnimationPhasePool` `0x80054AC8`
(closed s3634). That `$a0` is slot `+0x0`
(the header), not this interior. It is not
a second `jal rs_free` of `$s1`.

### Byte 2 — original free-source flag, always 0 on live objects

`uploadTextureDescriptorData` frees `$s1`
only when `0x2($s0)` bit 0 is set. Writers
of that byte on the converted header:

| Writer | PC | Value | Reachable on this object? |
|---|---|---|---|
| `fillTextureDescriptorNoCopy` | `0x80022FE0` | `sb $zero` | yes; only generated jal is `loadAssetIntoNewSlot` `0x800547FC`; `zmemcpy` publishes it |
| `loadAndDecodeTexture` dest-already-set | `0x80023060` | `sb $zero` | yes; delay-slot `sw` of the interior makes `0x0($a1)` nonzero, so the malloc-and-set-1 arm is not taken |
| `loadAndDecodeTexture` malloc-dest | `0x8002305C` | `sb 1` | no; dest is pre-stored |
| `copyTextureDescriptorWithData` malloc-src | `0x80022F10` | `sb 1` | no; zero generated jal, zero `LOOKUP_FUNC(0x80022E58)`, zero `lui`/`addiu` |

`copyTextureDescriptorWithData` is an
unreferenced clone of the "malloc a source
and set the free-source flag" formula. One
overlay-table entry (rom offset `0x22A18`,
size `0xF0`); the same generated body, not
a second body. That malloc never publishes
a descriptor that reaches this free.

`fillTextureDescriptorNoCopy` has no other
generated caller. `loadAndDecodeTexture`
has no other generated caller. Pool-side
functions that load `0x7C84` do not
`sb`/`sh` offset `0x2` of the header.
`blez` frame count skips
`loadAndDecodeTexture` and still leaves
byte 2 at 0 from the `zmemcpy`.

Failed converted malloc stores 0 at slot
`+0x0`. The tick would then pass
`0 + 0x14 + n*stride` and
`loadAndDecodeTexture` would `sb $zero` at
`0x2(NULL)`. That is the same unproven
allocator-failure edge s3604–s3650 left
open; `rs_free` of a nonzero interior of
NULL is not a live matching-allocator
path.

## Pairing

One generated `jal rs_free` of `$s1`. The
live caller always arrives with byte 2 = 0,
so the original skip is taken and `$s1` is
never passed to `rs_free`. The unreferenced
`copyTextureDescriptorWithData` malloc
cannot fire. Sequential double-free of the
interior would require the flag to be set;
no live writer sets it. The caller keeps
the header; `freeAnimationPhasePool` later
frees that header, a different pointer.
Runtime allocator legitimacy and whether
every converted malloc succeeds remain
unproven.

This `$s1` is not the s3636 overlay `0x1C`
/ `0x20` writer.

## Classification

The only `jal rs_free` site that can receive
this pointer is `0x800232CC`, and on every
live generated path the original byte-2 skip
prevents the call. `$s1` is an interior of
the `loadAssetIntoNewSlot` converted-buffer
malloc, not that malloc's stored return.
`copyTextureDescriptorWithData` is an
unreferenced clone of a matching
free-source allocator, not a second object
identity. All other loads are consumers
(memcpy source) or callee-save. Host
`MATERIAL_ARRAY_PTR_GUARD` is not an
original skip. This selects
`H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: the non-allocator
interior is never passed to `rs_free`.
`H-NextClassUnevaluable` is not selected:
one converted-buffer identity, one live
caller, one original skip that covers the
interior.

No guard was added. Runtime allocator state
remains unproven. The s3636 overlay skip-path
NULL store was not landed: this `$s1` is
not that writer.

## Next remaining `jal rs_free`

`funcs_6.c` original `jal 0x80001C98` is
exhausted. `funcs_5.c` has zero sites. The
next remaining original sites are in
`funcs_4.c`: `freeRenderSubsystemResources`
`0x80018668` (`$a0` = `*0x8011A444`,
`lui 0x8012; lw -0x5BBC`), then four
sibling globals in the same wrapper
(`*0x801163B4`, `*0x801143AC`,
`*0x8010E8A8`, `*0x8010E8AC`).
