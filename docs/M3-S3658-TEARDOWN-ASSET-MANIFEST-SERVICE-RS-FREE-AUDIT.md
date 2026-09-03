# M3 s3658 — teardownAssetManifestService rs_free of *0x80110D50

## Work unit

Static census of `teardownAssetManifestService`
`jal rs_free` at `0x80005000` (`$a0` =
`*0x80110D50` from `lw $a0, 0xD50($v0)`
at `0x80004FF4`, after `beq $a0, $zero`
skip at `0x80004FF8`). Enumerated every
original load/store of that
`*0x80110D50` (including the matching
allocator `initDmaSlots` `rs_malloc`
store at `0x80004708`, every later
store, whether the caller holds the
buffer, the NULL skip, and any sibling
`jal rs_free` of the same pointer or of
adjacent `0xD48`/`0xD4C`/`0xD54` words)
and every `jal rs_free` that can
receive that pointer. Other loads were
classified as consumers or as a second
free. No build or runtime run was
performed.

The word is not a caller-held buffer.
Absolute `0x80110D50` never appears in
generated code. The word is
`lui 0x8011; 0xD50`. Zero
`addiu 0xD50` / `0x10D50` aliases.
Zero gp-relative aliases.

The discriminator was the single complete
original census of that `jal rs_free`
site plus every original `lw`/`sw`/`addu`
of `teardownAssetManifestService`
`*0x80110D50` that can become this `$a0`,
every original `lw`/`sw` of the same
word, and every `jal rs_free` that can
receive that pointer. No overlay
duplicate of `teardownAssetManifestService`
/ `0x80004FD8` exists as a second
generated body.

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

Closed classes were not repeated. Do not
land a skip-path NULL store for the s3636
overlay Gap unless this census identifies
that same writer as this `*0x80110D50`.

## Census size

Original `jal 0x80001C98` in `funcs_1.c`:
7 sites. This census covers
`0x80005000`. `0x80003E7C` and
`0x8000450C` were closed together in
s3655 as `0x48($s0)`. `0x8000490C` was
closed in s3656 as the 8-byte header
scratch `$s2`. `0x80004A0C` and
`0x80004A80` were closed in s3657 as
DMA-slot `0x40($s0)`. Remaining:
`0x80005268` (`rs_zcfree`).
`funcs_3.c`, `funcs_5.c`, and
`funcs_0.c` have zero sites.
`funcs_2.c` / `funcs_4.c` /
`funcs_6.c` / `funcs_7.c` are exhausted.

`teardownAssetManifestService` is
`0x80004FD8`..`0x80005014`,
frame `-0x18`. Zero generated
`jal 0x80004FD8`. Zero
`LOOKUP_FUNC(0x80004FD8)`. Zero
`lui`/`addiu` function-pointer
constructions of `0x80004FD8`. One
overlay-table entry in `section_3_text`
(rom offset `0x4B98`, size `0x40`);
not a second generated body. Single
`jr $ra` at `0x80005010`.

## `*0x80110D50` — optional extra-heap base

`$s3` in `initDmaSlots` (`0x800045E8`)
is incoming `$a0`, the extra-heap size.
The only generated caller is boot
`0x800011EC` (`funcs_0.c`); the delay
slot is `addu $a0, $zero, $zero`. Zero
`LOOKUP_FUNC(0x800045E8)`. One
overlay-table entry in `section_3_text`
(rom offset `0x41A8`, size `0x20C`);
not a second generated body.

The extra-heap path is gated on
`lbu 0x31(*0x8010FCB0)`. That pointer
is the `getGameConfig` return
(`0x80037560`) stored at boot
`0x80001110`. If the byte is zero,
`initDmaSlots` stores 0 to `0xD4C`,
`0xD48`, and `0xD50`. If the byte is
nonzero and `$s3 == 0`, it stores 0 to
`0xD4C`/`0xD48` and does not write
`0xD50` (BSS-zero on first use). The
flags-0x81 malloc only runs when the
byte is nonzero and `$s3 != 0`. On
the generated caller `$s3` is 0, so
that malloc is an unreferenced original
branch, not a second generated body.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| extra-heap malloc | `0x800046F8`/`0x80004708` | `jal rs_malloc($s3, 0x81)`; `sw $v0, 0xD50($v1)` | `*0x80110D50` | live heap-pointer writer; `$s3 != 0` only |
| flag-zero skip | `0x8000471C` | `sw $zero, 0xD50($v0)` | `*0x80110D50` | explicit NULL |
| size copy | `0x800046E4` / `0x8000470C` | `sw $s3` / `sw $zero, 0xD4C` | `*0x80110D4C` | size, not this pointer |
| size word | `0x800046F0` / `0x80004714` | `sw $s3` / `sw $zero, 0xD48` | `*0x80110D48` | size passed as `$a1` |
| heap init | `0x80004724`/`0x80004730` | `lw $a0, 0xD50`; `jal initRsMallocHeap` | `*0x80110D50` | consumer; copies into `*0x80111260` |
| destructor | `0x80004FF4`/`0x80005000` | `lw $a0, 0xD50`; `beq $a0, $zero` skip; `jal rs_free` | `*0x80110D50` | destructor of the same word |
| worker handle | `0x800047D0` | `sw $a0, 0xD54` | `*0x80110D54` | `registerServiceWorker` return |

There is no `beq $v0, $zero` after the
extra-heap malloc. Failed malloc stores
0. `rs_free(0)` skips. That is the same
unproven allocator-failure edge
s3604–s3657 left open.

The destructor does not store NULL to
`0xD50` after a nonzero free. The
original `beq $a0, $zero` skip is the
NULL-pointer skip, not a post-free
clear. Missing NULL of the word is the
same unchecked-destructor shape already
closed as Complete for
`freeManifestSegmentAssets` (s3657),
`findManifestEntryByName` (s3656), and
`initSaveData` (s3653). The destructor
itself has zero generated callers, so a
second teardown cannot run on the
generated path.

### Consumers — heap init / worker handle, not a second free

| Function | PC | Use of D50 / adjacent |
|---|---|---|
| `initRsMallocHeap` | `0x80005380` | `$a0` is the extra-heap base; `$a1` is `*0x80110D48` size. If `$a0 == 0`, stores 0 to `*0x80111260` and returns. If nonzero, writes the arena header and stores the same pointer to `*0x80111260`. No `jal rs_free` |
| `getRsHeapMaxAllocSize` / `allocRsHeapBlock` | `0x800053F4` / `0x80005418` | `lw *0x80111260` as the arena base. Consumers of the alias, not a free of `*0x80110D50` |
| `teardownAssetManifestService` | `0x80004FDC` | `lw *0x80110D54` then `unregisterServiceWorker` (closed s3654). Different object |
| `setDmaWorkerPriority` | `0x80005364` | `lw *0x80110D54` then `setServiceWorkerPriority` |
| `submitDmaSlot` / `waitDmaSlotComplete` / `pollDmaSlotStep` / `mainEventQueueWorker` | `0x80003580` / `0x8000377C` / `0x80003958` / `0x80004534` / `0x800045D4` | `lw 0xD54` with `$s0`/`$s6`/`$s5` = `lui 0x8011`, then `yieldThreadRet1`. Worker-handle consumers |
| `findManifestEntryByName` and later DMA helpers | `0x80004BD4` / `0x80004C30` / `0x80004CB0` / `0x80004F18` / `0x80004F80` | `lw $a1, 0xD54($v0)` with `lui 0x8011`. Same worker handle |

`funcs_33.c` `sh $v0, 0xD50($s1)` at
`0x800C1EAC` is a halfword field of a
large `$s1` object (`addiu $s1, 0xD30`
and sibling `0xD28`..`0xD64` stores).
It is not `*0x80110D50`.

Host `rs64_m5_writer_parity` /
`rs64_probe_submit_gate_store` probes on
the stores are diagnostics, not original
skips.

## Sibling frees — different objects

`unregisterServiceWorker` at
`0x80004FE8` frees a list node from
`*0x801128D0` (closed s3654), not
`*0x80110D50`. Adjacent `0xD48`/`0xD4C`
are the extra-heap size; no
`jal rs_free` of those words exists.
`0xD54` is the service-worker handle;
no `jal rs_free` of that word exists.

`rs_zcfree` `0x80005268` is the zlib
wrapper. Its only generated caller is
`zcfree` `0x80029CFC` (`$a0` = incoming
`$a1`). It does not load `*0x80110D50`.

`freeManifestSegmentAssets` `0x40($s0)`
(closed s3657) is DMA-slot payload at
`0x80110A80 + idx*0x50 + 0x40`, not
this word.

## Callers — destructor is original-unreferenced

Zero generated `jal 0x80004FD8`. The
matching malloc is also original-
unreferenced on the generated boot
caller (`$a0 = 0`). `initRsMallocHeap`
therefore sees `$a0 = 0` (BSS-zero or
the explicit zero store) and does not
install an extra arena. That is one
destructor of one malloc store, with
both the publish and the free sitting
on unreferenced original branches, not
a second writer.

## Pairing

One extra-heap flags-0x81 malloc store,
one explicit NULL store on the flag-zero
path, one destructor of that word with
an original NULL skip. Adjacent
`0xD48`/`0xD4C`/`0xD54` are size and
worker-handle words, not this pointer.
`*0x80111260` is a consumer alias
written by `initRsMallocHeap`, not a
second free. Runtime allocator
legitimacy and whether a nonzero-size
caller of `initDmaSlots` exists outside
the generated tree remain unproven; the
generated tree has one caller and it
passes 0.

This `*0x80110D50` is not the s3636
overlay `0x1C`/`0x20` writer.

## Classification

The only `jal rs_free` site that can
receive this `*0x80110D50` is
`0x80005000`. The only live original
heap-pointer writer is the flags-0x81
`rs_malloc` store at `0x80004708`. All
other uses are the explicit NULL store,
the `initRsMallocHeap` consumer, the
`*0x80111260` alias consumers, or
adjacent size/worker-handle words.
This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static
scope. `H-NextClassUnevaluable` is not
selected: one word, one malloc store,
one destructor.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: this
`*0x80110D50` is not that writer.

## Next remaining `jal rs_free`

The next remaining original site is
`funcs_1.c` `rs_zcfree` `0x80005268`
(`$a0` = incoming `$a0` after
`beq $a0, $zero` skip). That is the
last original `jal 0x80001C98` in
`funcs_1.c`.
