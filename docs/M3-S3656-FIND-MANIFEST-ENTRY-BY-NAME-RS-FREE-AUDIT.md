# M3 s3656 — findManifestEntryByName rs_free of $s2

## Work unit

Static census of `findManifestEntryByName`
`jal rs_free` at `0x8000490C` (`$a0` =
`$s2` from `addu $a0, $s2` at
`0x80004900`). Enumerated every original
load/store of that `$s2` (including the
matching allocator, every later store,
whether the caller holds the buffer, the
delay-slot `lw $s2, 0x0($a0)` at
`0x80004908` / `and $s0, $s0, $v0` at
`0x80004910`, and any sibling
`jal rs_free` of the same pointer or of
adjacent words) and every `jal rs_free`
that can receive that pointer. Other
loads were classified as consumers or as
a second free. No build or runtime run
was performed.

`$s2` is not a caller-held buffer. It is
the return of `rs_malloc(8, 9)` at
`0x800048A4`, kept in `$s2` at
`0x800048AC`. It is never stored to a
global or to a DMA-slot word. Incoming
`$a0` is a ROM name string in `$s3` and
is not this pointer.

The discriminator was the single complete
original census of that `jal rs_free`
site plus every original `lw`/`sw`/`addu`
of `findManifestEntryByName` `$s2` that
can become this `$a0`, and every
`jal rs_free` that can receive that
pointer. No overlay duplicate of
`findManifestEntryByName` / `0x800047F4`
exists as a second generated body.

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
that same writer as this `$s2`.

## Census size

Original `jal 0x80001C98` in `funcs_1.c`:
7 sites. This census covers
`0x8000490C`. `0x80003E7C` and
`0x8000450C` were closed together in
s3655 as `0x48($s0)`. Remaining:
`0x80004A0C`, `0x80004A80`,
`0x80005000`, `0x80005268`.
`funcs_3.c`, `funcs_5.c`, and
`funcs_0.c` have zero sites.
`funcs_2.c` / `funcs_4.c` /
`funcs_6.c` / `funcs_7.c` are exhausted.

`findManifestEntryByName` is
`0x800047F4`..`0x80004994`,
frame `-0x30`. Six generated
`jal 0x800047F4`:
`loadDebugAssets` `0x80024720`
(`$a0` = `0x80000A3C`),
`mainGameLoop` `0x8003E2A8` and
`0x8003E36C` (`$a0` = `0x8003A3E0`),
`runIdleFramesAndLoadSaveData`
`0x8006D9D8` (`$a0` = `0x8003CAF0`),
`initSceneForMission` `0x800A9C7C`
(`$a0` = `0x800A5408`),
`menuOverlayInit` `0x800C5A2C`
(`$a0` = `0x800A7560`). All six pass
ROM string literals. Zero
`LOOKUP_FUNC(0x800047F4)`. Zero
`lui`/`addiu` function-pointer
constructions of `0x800047F4`. One
overlay-table entry in `section_3_text`
(rom offset `0x43B4`, size `0x1A0`);
not a second generated body. Single
`jr $ra` at `0x8000498C`.

## `$s2` — 8-byte header scratch

`$s2` is first `0x80110000` for the
name-table `lw 0xA74` strcmp walk, then
overwritten by the malloc return. The
prologue `sw $s2, 0x18($sp)` saves the
caller's `$s2`; the epilogue restores
it. Neither is the freed pointer.

The name table is `*0x80110A74`,
0x20-stride, count `*0x80110D40`.
`initDmaSlots` `rs_malloc($s0=0x40, 0x81)`
at `0x8000476C` stores that pointer at
`0xA74` and DMA-fills it from cart
`0xB0144340` (`submitDmaSlot` dest =
the table, size `0x40`). Count is
`0x40>>5` = 2. Entry `+0x18` and `+0x1C`
are ROM words, not this `$s2`.

DMA slots are BSS `0x80110A80`, 0x50
stride, four entries. `$s1` starts at
that base; `$s4` is the free-slot index
from `lbu 0x4E == 0`. `$s3` becomes
`0x80110A80 + $s4*0x50` after the malloc.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc 8 | `0x800048A4`/`0x800048AC` | `jal rs_malloc(8, 9)`; `addu $s2, $v0` | `$s2` | live heap-pointer writer |
| DMA dest | `0x800048D8` | `addu $a1, $s2` | `$s2` | `submitDmaSlot` dest; size 8; src `*0x80110D44 + entry+0x1C` |
| destructor | `0x80004900`/`0x8000490C` | `addu $a0, $s2`; `jal rs_free` | `$s2` | destructor of the 8-byte malloc |
| header word 0 | `0x80004908` | `lw $s2, 0x0($a0)` | `$s2` overwritten | consumer; ROM offset, not a pointer |
| header word 1 | `0x80004904`/`0x80004910` | `lw $s0, 0x4($s2)`; `and 0x7FFFFFFF` | `$s0` | size for the payload malloc |
| payload malloc | `0x80004918`/`0x80004920` | `jal rs_malloc($s0, 9)`; `sw $v0, 0x40($s3)` | slot+0x40 | different pointer; not this `$s2` |
| skip | `0x800048D0` | `bne entry+0x18, L_8000496C` | `$s2` leaked | no free; ROM `+0x18` is not this pointer |

There is no `beq $v0, $zero` after the
8-byte malloc. Failed malloc leaves
`$s2` = 0. `rs_free(0)` skips. That is
the same unproven allocator-failure edge
s3604–s3655 left open. The skip path
does not load through `$s2`.

The `lw $s2, 0x0($a0)` at `0x80004908`
runs before the `jal`. `$a0` already
holds the malloc pointer, so the free
argument is still the 8-byte buffer.
After the free, `$s2` is the header
offset and is added into the payload DMA
src (`addu $a0, $a0, $s2` at
`0x80004954`). That is not `jal rs_free`.

The skip when `entry+0x18 != 0` returns
`$s4` without freeing `$s2` and without
storing it. That is an 8-byte leak of a
never-published pointer, not a second
free. Same shape as the s3653 re-init
leak. `entry+0x18` is a ROM-DMA'd name-
table word; this function never stores
`$s2` there.

### Consumers — DMA dest / header words, not a second free

| Function | PC | Use after `$s2` = malloc |
|---|---|---|
| `findManifestEntryByName` | `0x800048D8` | `submitDmaSlot` dest (`$a1`) |
| `findManifestEntryByName` | `0x80004904` | `lw 0x4($s2)` size |
| `findManifestEntryByName` | `0x80004908` | `lw 0x0($a0)` offset into `$s2` |
| `findManifestEntryByName` | `0x80004954` | payload DMA src addend (offset) |

`submitDmaSlot`, `waitDmaSlotComplete`,
`pollDmaSlotStep`, and `teardownAssetDma`
have zero `jal rs_free`. Host
`rs64_m5_writer_parity` /
`rs64_probe_submit_gate_store` probes on
the stores are diagnostics, not original
skips.

## Sibling frees — different objects

`freeManifestSegmentAssets` `0x80004A0C`
and `0x80004A80` load `0x40($s0)` of the
0x50-stride DMA slots at `0x80110A80`.
That word is the payload malloc stored
at `0x80004920` after this 8-byte buffer
has already been freed. It is not this
`$s2`. Those sites are the next unit.

`teardownAssetManifestService`
`0x80005000` frees `*0x80110D50`
(`initDmaSlots` flags-0x81 heap).
`rs_zcfree` `0x80005268` is the zlib
wrapper. Neither receives this `$s2`.

## Pairing

One register-local 8-byte flags-9 malloc,
one destructor of that pointer, never
stored. The skip path leaks; it does not
free a second time. There is no third
`jal rs_free` of this pointer. Same
unchecked-NULL destructor shape already
closed as Complete for
`processAssetLoadStep` (s3655) and
`initSaveData` (s3653). Runtime allocator
legitimacy and whether every call's
malloc succeeds remain unproven.

The skip-path leak is not the s3636
skip-path Gap: s3636 freed words that
setup never stored. This skip leaves an
unpublished 8-byte buffer unfreed.

## Classification

The only `jal rs_free` site that can
receive this `$s2` is `0x8000490C`. The
only live original heap-pointer writer is
the flags-9 `rs_malloc(8)` at
`0x800048A4`. All other uses are DMA dest
or header-word consumers, or the ROM
`+0x18` skip that never frees. Adjacent
slot `+0x40` is a different malloc.
This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static
scope. `H-NextClassUnevaluable` is not
selected: one register-local buffer, one
malloc, one destructor.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: this
`$s2` is not that writer.

## Next remaining `jal rs_free`

The next remaining original site is
`funcs_1.c` `freeManifestSegmentAssets`
`0x80004A0C` (`$a0` = `0x40($s0)` from
`lw $a0, 0x40($s0)` at `0x80004A08`).
Sibling `0x80004A80` loads the same
word. Four sites remain in that file.
