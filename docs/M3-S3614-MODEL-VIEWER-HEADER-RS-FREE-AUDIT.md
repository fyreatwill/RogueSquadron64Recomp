# M3 s3614 — remaining lookup-table header rs_free in shutdownModelViewer

## Work unit

Static census of every generated original `jal rs_free` in
`shutdownModelViewer`. Remaining lookup-table header frees after
the closed funcs_14 lookup-table class: `0x800CBB58` of
`0x800D0364` and `0x800CBB68` of `0x800D0360` (the two
`initModelViewer` `allocateSlotTable` returns). Also classified
the sibling `0x800CBB40` free of `0x800D03CC` in the same
function. Classified every original `sw` of each pointer and
whether a free can run on a non-allocator or already-freed
value, including whether these header-word frees skip
`destroyLookupTable` and leak `0x0(header)`. No build or runtime
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

Closed classes were not repeated: lookup-table, loadCharTextureSet
DMA-array, load_asset-then-free, texture-scratch `rs_free`,
text-texture `rs_free`, format-message `rs_free`, speech-file
`rs_free`, speech/cache `rs_free`, destructor skipped-NULL,
destructor unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `shutdownModelViewer`: three sites,
all this class. `funcs_37.c` still has later `rs_free` in
`freeModelViewerMeshChain`, `tickMultiPartVoiceLine`,
`npcAtAtUpdate`, `npcAtStUpdate`, and `playerAtStUpdate`.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| model-viewer lookup A | `0x800D0360` | `initModelViewer` delay-slot `sw $v0, 0x360($s0)` `0x800CA6D0`; `$s0=0x800D` | first `allocateSlotTable(8)` `0x800CA6BC` (header `rs_malloc(8)`) | `0x800CBB68` of `$a0`; no skip, no post-free NULL |
| model-viewer lookup B | `0x800D0364` | `initModelViewer` delay-slot `sw $v0, 0x364($v1)` `0x800CA6EC`; `$v1=0x800D` | second `allocateSlotTable(8)` `0x800CA6CC` | `0x800CBB58` of `$a0`; no skip, no post-free NULL |
| model-viewer dat file | `0x800D03CC` | `initModelViewer` `sw $v0, 0x3CC($v1)` `0x800CA708` after `loadDatFile` | `load_asset` `rs_malloc` captured in `$s2` (`0x800648DC`), returned as `$v0` (`0x80064914`); `loadDatFile` returns that `$s2` or `0` | `0x800CBB40` of `$a0`; no skip, no post-free NULL |

Those three `sw $v0` are the only original stores of those words.
No `sw $zero`. `rs_free` itself `beq $s0, $zero` and returns, so
a NULL word is a skip, not a Gap.

## Remaining function

### `shutdownModelViewer` (`0x800CBB30`) — three frees

Frame is `-0x18`. `$v0` is `lui 0x800D` before each load. Order:

1. `lw $a0, 0x3CC($v0)` then `jal rs_free` at `0x800CBB40`.
2. `jal resetPlayerSlotChannelTransform` with `$a0=3`
   (`0x80063BEC`; starts `lui 0x800A`, does not load these words).
3. `lw $a0, 0x364($v0)` then `jal rs_free` at `0x800CBB58`.
4. `lw $a0, 0x360($v0)` then `jal rs_free` at `0x800CBB68`.
5. One `jr $ra`.

No generated path reaches the return without the three frees.
None of the three words is NULLed. The function never `jal
0x80064628` (`destroyLookupTable`).

## Matching init

### `initModelViewer` (`0x800CA638`) — only writer

`jal allocateSlotTable(8)` at `0x800CA6BC`. The delay slot of
the second `jal allocateSlotTable(8)` at `0x800CA6CC` is
`sw $v0, 0x360($s0)`, so `0x800D0360` is the first header.
The delay slot of `jal loadCharTextureSet` at `0x800CA6E8` is
`sw $v0, 0x364($v1)`, so `0x800D0364` is the second header.
`loadCharTextureSet` receives `$a0=0x800D0360` and does not
`jal rs_free` (closed s3612).

`jal loadDatFile(0x800A79D0)` at `0x800CA6F4` then
`sw $v0, 0x3CC($v1)`. `loadDatFile` (`0x80046784`) does
`jal load_asset` (`0x8006488C`) and keeps that return in `$s2`.
`load_asset` `jal rs_malloc` at `0x800648C0` and rebinds `$s2`
to `$v0` at `0x800648DC`. The only `loadDatFile` path that
returns the asset is `j L_80047334` at `0x80046DA0` with delay
slot `addu $v0, $s2, $zero` when `lbu 0x80130B3A != 1`. The
other epilogue edges set `$v0=0`. `load_dat_file_assets`
(`0x80064940`) has no `jal rs_free`. A NULL `0x800D03CC` is
the skip `rs_free` already allows.

## Consumers — do not free these words

Every original `lw` of `0x360`/`0x364`/`0x3CC` uses `lui 0x800D`
(including `loadModelViewerModels` `$s7` at `0x800CB644` and
`$fp` at `0x800CB860`; no `$fp` rewrite before `0x800CB924`).

| Word | Loads | Callee |
|---|---|---|
| `0x800D0360` | `0x800C9D00` | `findLookupEntryByKey` |
| | `0x800C9DBC` | `rebuildActiveDisplayObjectList` |
| | `0x800CA45C` | `setLookupEntryField5ByKey` |
| | `0x800CA6E0` | `loadCharTextureSet` (init) |
| `0x800D0364` | `0x800C9E4C` | `rebuildActiveDisplayObjectList` |
| | `0x800CA4EC` | `accumulateShipThrottleCharge` |
| | `0x800CA558` | `updateTextOverlayLookupEntry` |
| | `0x800CA5A4` | `destroyPlayerShipRecord` (exit path; `jal removeLookupTableEntry`, no `jal rs_free`) |
| `0x800D03CC` | `0x800CB70C` | `getDatItemByName` |
| | `0x800CB924` | `findDatItemInTableByName` |

Those callees have no `jal rs_free`. `findLookupEntryByKey` /
`removeLookupTableEntry` / `rebuildActiveDisplayObjectList`
write slot records inside `0x0(header)`, not the header word
(s3613).

## Pairing / double-free / leak of `0x0(header)`

The only generated `jal 0x800CA638` / `jal 0x800CBB30` is
`runModelViewerLoop`: init once after prologue, shutdown once
on the epilogue path after `releaseModelViewerModelAssets` /
`freeModelViewerMeshChain`, then `jr $ra` at `0x800CA630`.
No `lui`/`ori`/`addiu` constructs either address. The only
`jal 0x800C9BF0` is `menuOverlayInit` `0x800C5C34`, which then
jumps away.

Sequential double-free of these three words is blocked by that
single init/shutdown pair. Sequential double-free through
`destroyLookupTable` is blocked by the missing caller (s3613).
Re-init without shutdown leaks the previous header and slots.
A first-malloc failure would store NULL and `rs_free` would
skip. Those are the same unproven re-init / allocator edges
s3604–s3613 left open, not a second pointer source.

The two header frees skip `destroyLookupTable` and never load
`0x0(header)`. Each `allocateSlotTable(8)` also `rs_malloc`s
the 64-byte slots array and stores it at `0x0(header)`. That
slots word is leaked when shutdown frees only the header. A
leak is a missing destructor of a different pointer, not a
free of a non-allocator or already-freed value for these three
sites.

No other generated `jal rs_free` loads the remaining
`allocateSlotTable` header globals from s3613
(`0x800CD668`, `0x800B0AFC`/`0x800B0B00`, `0x800CDCDC`,
`0x800CF078`/`0x800CF07C`/`0x800CF080`).

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted
at static scope. `H-NextClassUnevaluable` is not selected: the
three pointers are the two `allocateSlotTable` headers and the
`loadDatFile`/`load_asset` return (or NULL).
