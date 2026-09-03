# M3 s3657 — freeManifestSegmentAssets rs_free of 0x40($s0)

## Work unit

Static census of `freeManifestSegmentAssets`
`jal rs_free` at `0x80004A0C` (`$a0` =
`0x40($s0)` from `lw $a0, 0x40($s0)` at
`0x80004A08`). Included the sibling
`jal rs_free` at `0x80004A80` (`lw $a0,
0x40($s0)` at `0x80004A7C`) in the same
census: both load the 0x50-stride DMA-slot
word at `0x80110A80 + idx*0x50 + 0x40`.
Enumerated every original load/store of
that `0x40($s0)` (including the matching
allocator `findManifestEntryByName`
`rs_malloc` store at `0x80004920`, every
later store, whether the caller holds the
buffer, the post-free `sb $zero, 0x4E($s0)`
busy-clear, and any sibling `jal rs_free`
of the same pointer or of adjacent slot
words) and every `jal rs_free` that can
receive that pointer. Other loads were
classified as consumers or as a second
free. No build or runtime run was
performed.

`$s0` is not a caller-held buffer. It is
the DMA-slot row `0x80110A80 + idx*0x50`
(`lui 0x8011; addiu 0xA80`, stride
`*5<<4` = `0x50`, four slots). Incoming
`$a0` is either `-1` (all-slots walk) or
a slot index. The freed word is
`0x40($s0)`, the payload pointer.

The discriminator was the single complete
original census of those two `jal rs_free`
sites plus every original `lw`/`sw`/`addu`
of `freeManifestSegmentAssets` `0x40($s0)`
that can become this `$a0`, every original
`lw`/`sw` of the same slot field, and
every `jal rs_free` that can receive that
pointer. No overlay duplicate of
`freeManifestSegmentAssets` / `0x80004994`
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
that same writer as this `0x40($s0)`.

## Census size

Original `jal 0x80001C98` in `funcs_1.c`:
7 sites. This census covers
`0x80004A0C` and `0x80004A80`.
`0x80003E7C` and `0x8000450C` were closed
together in s3655 as `0x48($s0)`.
`0x8000490C` was closed in s3656 as the
8-byte header scratch `$s2`. Remaining:
`0x80005000`, `0x80005268`.
`funcs_3.c`, `funcs_5.c`, and
`funcs_0.c` have zero sites.
`funcs_2.c` / `funcs_4.c` /
`funcs_6.c` / `funcs_7.c` are exhausted.

`freeManifestSegmentAssets` is
`0x80004994`..`0x80004AA8`,
frame `-0x28`. Six generated
`jal 0x80004994`:
`loadDebugAssets` `0x8002482C`
(`$a0` = `$s4`, the find return),
`mainGameLoop` `0x8003E2D4` and
`0x8003E398` (`$a0` = `*0x80137CFC`),
`runIdleFramesAndLoadSaveData`
`0x8006DA84` (`$a0` = `*0x80137CFC`),
`freeCutsceneResources` `0x800AEB50`
(`$a0` = `*0x80137CFC`),
`menuOverlayInit` `0x800C5D0C`
(`$a0` = `*0x80137CFC`). Zero
`LOOKUP_FUNC(0x80004994)`. Zero
`lui`/`addiu` function-pointer
constructions of `0x80004994`. One
overlay-table entry in `section_3_text`
(rom offset `0x4554`, size `0x118`);
not a second generated body. Single
`jr $ra` at `0x80004AA4`.

## `0x40($s0)` — DMA-slot payload pointer

`$s0` is `0x80110A80` on the all-slots
path (`$a0 == -1`) and
`0x80110A80 + $a0*0x50` on the
single-slot path. The two `jal rs_free`
sites are mutually exclusive: the
prologue `bne $a0, -1, L_80004A2C`
takes exactly one. After each free the
original code `sb $zero, 0x4E($s0)`
clears busy; it does not store NULL to
`0x40`. The all-slots walk only frees
when `lbu 0x4E == 1`. The single-slot
path does not test `0x4E`.

`initDmaSlots` walks the same four
rows backward from `0x80110A80+0xF0`
and zeros `0x4E` only. BSS zeros
`0x40` at boot. `addiu 0xA80` lives
only in `funcs_1.c`.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| payload malloc | `0x80004918`/`0x80004920` | `jal rs_malloc($s0, 9)`; `sw $v0, 0x40($s3)` | slot+0x40 | live heap-pointer writer |
| busy set | `0x8000492C` | `sb 1, 0x4E($s3)` | slot+0x4E | pairs the store |
| all-slots free | `0x80004A08`/`0x80004A0C` | `lw $a0, 0x40($s0)`; `jal rs_free` | slot+0x40 | destructor; gated by `0x4E==1` |
| all-slots busy-clear | `0x80004A14` | `sb $zero, 0x4E($s0)` | slot+0x4E | original skip for a later all-slots walk |
| single-slot free | `0x80004A7C`/`0x80004A80` | `lw $a0, 0x40($s0)`; `jal rs_free` | slot+0x40 | destructor of the same word |
| single-slot busy-clear | `0x80004A88` | `sb $zero, 0x4E($s0)` | slot+0x4E | same skip |
| directory walk | `0x80003AC8` | `lw $s2, 0x40($v0)` | slot+0x40 | consumer; name table inside the payload |
| skip `+0x18` | `0x800048D0` | `bne entry+0x18, L_8000496C` | no store | does not publish `0x40` |

There is no `beq $v0, $zero` after the
payload malloc. Failed malloc stores 0.
`rs_free(0)` skips. That is the same
unproven allocator-failure edge
s3604–s3656 left open.

The skip when name-table `entry+0x18
!= 0` returns the free-slot index
without storing `0x40`. Both ROM
entries DMA'd by `initDmaSlots` from
cart `0xB0144340` have `+0x18 = 0`
(`data` and `dbg_data`). The skip
does not fire on this ROM. If it
fired, a later single-slot free would
see BSS-zero or a stale word; first
use is `rs_free(0)`.

`findManifestEntryByName` never
returns `-1`. `loadDebugAssets`
skips the free when `$s4 == -1`;
that compare is dead. No generated
caller passes `-1`, so the all-slots
path is an unreferenced original
branch, not a second generated body.

### Consumers — directory walk / dest / size, not a second free

| Function | PC | Use of slot+0x40 / adjacent |
|---|---|---|
| `find_manifest_entry` | `0x80003AC8` | `lw 0x40` as directory base; `strncmp` at `+0x10`; returns an interior pointer; no `jal rs_free` |
| `find_manifest_entry` | `0x80003ACC` | `lw 0x48` entry count (`size>>5`) |
| `findManifestEntryByName` | `0x80004924` | payload DMA dest (`$a1` = malloc return) |
| `findManifestEntryByName` | `0x80004948` / `0x80004960` | `sw size>>5, 0x48`; `sw cart-src, 0x44` |
| `resolveAssetRamAddress` | `0x8000532C` | `lw 0x44` cart-src, not `0x40` |
| `get_asset_size_extra` / `get_manifest_entry_type` / `get_asset_size_simple` / `findAssetAcrossSegments` | `0x4E` tests | busy consumers; no `lw 0x40` |
| `processOverlayDmaStruct` | `0x800033D0` | `lw 0x40($s0)` of a different incoming overlay DMA struct, stride 4, not `0x80110A80` |

`submitDmaSlot`, `waitDmaSlotComplete`,
`pollDmaSlotStep`, and `teardownAssetDma`
have zero `jal rs_free`. Host
`rs64_m5_writer_parity` /
`rs64_probe_submit_gate_store` probes on
the stores are diagnostics, not original
skips. `processAssetLoadStep` `0x48($s0)`
is `D_80110D60 + idx*0x74 + 0x48`
(closed s3655), not this word.

## Sibling frees — different objects

`findManifestEntryByName` `0x8000490C`
frees the 8-byte header scratch `$s2`
before the payload malloc is stored
(closed s3656). It is not this `0x40`.

`teardownAssetManifestService`
`0x80005000` frees `*0x80110D50`
(`initDmaSlots` flags-0x81 heap).
`rs_zcfree` `0x80005268` is the zlib
wrapper. Neither receives this `0x40`.

## Callers — find-then-free of the slot index

`*0x80137CFC` writers are the find
return: `runIdleFramesAndLoadSaveData`
`0x8006D9EC`, `mainGameLoop`
`0x8003E2B8` / `0x8003E37C`,
`initSceneForMission` `0x800A9C90`,
`menuOverlayInit` `0x800C5A3C`. No
store of `-1`. `loadDebugAssets` keeps
the return in `$s4` and frees that.
`initSceneForMission` stores and does
not free in-function;
`freeCutsceneResources` (from
`cinematicLoopBody` `0x800A64F4`) is
the delayed destructor of that leftover
index. That is one destructor wrapper
with a cross-function pair, not a
second writer.

## Pairing

One DMA-slot payload flags-9 malloc
store, two mutually exclusive
destructors of that word, one
directory-walk consumer. The skip path
does not fire on this ROM and does not
store this pointer. Busy-clear of
`0x4E` is the original all-slots skip;
missing NULL of `0x40` is the same
unchecked-destructor shape already
closed as Complete for
`findManifestEntryByName` (s3656) and
`initSaveData` (s3653). Runtime
allocator legitimacy and whether every
call's malloc succeeds remain unproven.

This `0x40` is not the s3636 overlay
`0x1C`/`0x20` writer.

## Classification

The only `jal rs_free` sites that can
receive this `0x40($s0)` are
`0x80004A0C` and `0x80004A80`. The
only live original heap-pointer writer
is the flags-9 `rs_malloc` store at
`0x80004920`. All other uses are the
directory-walk consumer, DMA dest /
`0x44`/`0x48`/`0x4E` fields, or the
ROM-dead `+0x18` skip that never
stores. Adjacent slot words are not
this pointer. This selects
`H-NextClassComplete`.
`H-NextClassGap` is refuted at static
scope. `H-NextClassUnevaluable` is not
selected: one slot field, one malloc
store, two mutually exclusive
destructors.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: this
`0x40($s0)` is not that writer.

## Next remaining `jal rs_free`

The next remaining original site is
`funcs_1.c` `teardownAssetManifestService`
`0x80005000` (`$a0` = `*0x80110D50`
from `lw $a0, 0xD50($v0)` at
`0x80004FF4`). One site remains after
that (`rs_zcfree` `0x80005268`).
