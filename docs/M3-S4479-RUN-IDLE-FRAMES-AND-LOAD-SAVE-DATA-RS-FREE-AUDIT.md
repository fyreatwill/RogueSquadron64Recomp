# M3 s4479 — runIdleFramesAndLoadSaveData rs_free of the gamesave asset

## Work unit

Static census of the one original `jal rs_free` in
`runIdleFramesAndLoadSaveData` (`0x8006D900`, size `0x22C`), at
`0x8006DA28`, which forwards `$s0` in the delay slot. No build or
runtime run was performed. `initSaveData` (s3653) and
`load_naboo_starfighter` (s4478) were not re-audited.

The discriminator was that one site plus every original assignment
of `$s0` inside the function, every callee that could free the
same pointer, and every caller that could supply it:

- H-NextClassGap: the free can receive a pointer that is not the
  matching `rs_malloc` return, or can free it again after a
  sibling already released it.
- H-NextClassComplete: the only freed value is that allocator
  return, freed once, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, so the writer cannot be named.

Same-scan positive control: the `jal 0x80001C98` comment pattern
still locates closed `0x8006B814` and `0x8006C8C4` in `funcs_16.c`
(also `0x8006C4A8` and `0x8006C650`) and `0x80005268` in
`funcs_1.c`, and locates this site in `funcs_17.c`. The ROM word
for that jal is `0x0C000726`. It matches `0x8006B814`,
`0x8006C8C4`, `0x80005268`, and `0x8006DA28`. The cart bytes at
`0x8003C960` and `0x8003C9B0` are still `pl_crafts/shadows_TM` and
`pl_crafts/koelsch_HMT`.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_17.c`, `0x8006DA28` | `$s0` | `addu $s0, $v0` at `0x8006DA00` after `jal load_asset` `0x8006D9F8` | sole free; matching allocator return |

`$s0` is written six times in the ROM function. The generated
listing has the same six PCs.

| PC | Instruction | Reaches the free? |
|---|---|---|
| `0x8006D924` | `addu $s0, $zero, $zero` | no; loop counter, overwritten |
| `0x8006D984` | `addiu $s0, $s0, 1` | no; same counter, overwritten |
| `0x8006DA00` | `addu $s0, $v0, $zero` | yes; this is the freed value |
| `0x8006DA88` | `addu $s0, $zero, $zero` | no; after the free |
| `0x8006DAC4` | `addiu $s0, $s0, 1` | no; second idle loop, after the free |
| `0x8006DB20` | `lw $s0, 0x70($sp)` | no; epilogue, after the free |

The first loop exits through `bne` at `0x8006D9B4` to the linear
block that calls `load_asset`. Its back-edge is `0x8006D980`, not
the free. There is no `jr` before `0x8006DA28`. The only branch
to `0x8006DA28` is `bne` at `0x8006DA18`, and both of its paths
are after `0x8006DA00`. That `bne` is not likely, so its delay
slot `lui $v1, 0x8013` always runs and does not write `$s0`. The
not-taken path stores `1` at `0x80130B6C` and also does not write
`$s0`. Nothing between `0x8006DA00` and the free assigns `$s0`.

`$v0` at `0x8006DA00` is the `load_asset` return. `load_asset`
(`0x8006488C`, size `0xA8`) is straight-line. It copies the name
into `$s2`, calls `get_asset_size_extra`, calls `rs_malloc` with
that size and flags `0`, then `addu $s2, $v0` at `0x800648DC`.
`addu $v0, $s2` at `0x80064914` runs before the epilogue reloads
`$s2`. There is no branch and no `jal rs_free` in the function.

## What the block is

`findManifestEntryByName` is called with `$a0 = 0x8003CAF0`, the
ROM string `data`. Its return is stored at `0x80137CFC`. That
word is not `$s0`. `load_asset` is then called with
`$a0 = 0x8003CAF8`, the ROM string `gamesave`. `load_asset`
reads `0x80137CFC` as the manifest argument to
`findAssetAcrossSegments`. It does not return that word.

`get_asset_size_extra`, `findAssetAcrossSegments`,
`setupAssetDma`, `teardownAssetDma`, and `memcpy` (`0x800346F0`)
contain zero `jal rs_free` and zero `jalr` in their symbol
ranges. `rs_malloc` is the producer. `setupAssetDma` copies the
block to `0x24($a2)` from the stack argument at caller `0x14($sp)`
(`lw` at callee `0x80004EF4`, `sw` at `0x80004F04`) and does not
free it. `teardownAssetDma` stores at offsets `0`, `0x10`,
`0x14`, and `0x18` of its record and does not read offset
`0x24`. A scan of `lw` of offset `0x24` in the mapped image from
`0x80000400` through `0x80200000` found no site that moves that
load into `$a0` and then executes `jal rs_free` within the next
14 instructions.

`initSaveData` (`0x80006338`) receives this `$s0` as `$a0` and
`classifySaveStateFromInput` (`0x8006F0B8`) as `$a1`. The first
instructions copy `$a0` to `$v1` and pass `$v1` as the source of
`memcpy` of `0x20` bytes into `0x801126C0`. They store `$a1`, not
the buffer, at `0x801126F0`. The sole `jr` is `0x8000675C`. Its
epilogue reloads `$s0` from `0x30($sp)`, and the matching store
is the delay slot of the unconditional `jal memcpy` at
`0x8000636C`, so the caller's `$s0` is saved before `initSaveData`
uses `$s0` and is restored on every return. The two `jal rs_free`
inside `initSaveData` (`0x8000671C`, `0x8000672C`) free its own
`$s2`, the `rs_malloc` at `0x800065E8`. `$a0` for the first is
set by `addu $a0, $s2` at `0x80006708`; the second sets it in
the delay slot. Neither is this buffer. The `jalr` sites call
`0x801126F0` with `$a0` equal to `2`, `8`, or `9`.
`classifySaveStateFromInput` has no `jal` and no `jalr`. When
`$a0 == 8` it stores a byte at `0x8013A5B0` and returns `2`.

`freeManifestSegmentAssets` at `0x8006DA84` loads `$a0` from
`0x80137CFC` (the `data` manifest return) and zeros `$s0` only
in that jal's delay slot, after the gamesave free. That free is
the object closed in s3657, not this `$s0`.

A NULL `rs_malloc` return would make `$s0` zero. `initSaveData`
would then `memcpy` from NULL before this free. That is the same
unproven allocator-failure edge left open by s3604–s4478, not a
second pointer identity. The generated function has no range
check that substitutes a different `$s0`.

## Callers

One definition. One generated call. One uncompressed-ROM hit of
the jal word `0x0C01B640`, at file offset `0x3EC10`, which is
VRAM `0x8003E010`.

| Caller | Site | Argument |
|---|---|---|
| `mainGameLoop` | `0x8003E010` | none; delay slot is `nop` |

The call sits after `loadOverlay` of argument `1`. It does not
write `$a0`. This function saves the caller's `$s0` at
`0x8006D91C` and restores it at `0x8006DB20`, so the gamesave
pointer does not escape in `$s0`. The pointer is not stored by
this function. The return value is whatever
`applyAccountUnlocksToSettings` leaves in `$v0`.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static scope:
the freed register is only the `load_asset` / `rs_malloc` return
of `gamesave`, no callee frees that pointer, and this function
frees it once. The earlier `$s0` values are the 32-iteration
idle counter and do not reach the free. H-NextClassUnevaluable
is not selected. Runtime allocator and freelist legitimacy
remain unproven. No guard was added.

The next unaudited `jal rs_free` in address order is
`saveServiceWorker` at `0x8006F378` (`$a0 = $s0`, entry
`0x8006F2CC`). `$s0` is assigned from `$v0` at `0x8006F334`
after `jal 0x80006F24`, and `0x8006F380` jumps back to
`0x8006F318`. The `beql` at `0x8006F370` writes a byte through
`$s2` on the taken path only. It does not write `$s0`. Do not
treat the incoming `$a0` (saved in `$s5` at `0x8006F2D4`) as
the freed pointer without showing that the rebind does not
dominate.
