# M3 s4477 — loadCraftShadowTextures rs_free of the shadows asset

## Work unit

Static census of the one original `jal rs_free` in
`loadCraftShadowTextures` (`0x8006B710`), at `0x8006B814`, which
forwards `$s5` in the delay slot. s3620 and s3621 named this
function as a leftover after the NPC-destructor classes and never
classified it. No build or runtime run was performed.

The discriminator was that one site plus every original assignment
of `$s5` inside the function, every callee that could free the
same pointer, and every caller that could supply it:

- H-NextClassGap: the free can receive a pointer that is not the
  matching `load_asset` return, or can free it again after a
  sibling already released it.
- H-NextClassComplete: the only freed value is that allocator
  return, freed once, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, so the writer cannot be named.

Same-scan positive control: the `jal 0x80001C98` comment pattern
that located `0x8006B814` in `funcs_16.c` also locates the already
closed sites `0x80005268` (`rs_zcfree`, s3790, `funcs_1.c`) and
`0x800AEA94` (`hangarLoadShadows`, s3611, `funcs_29.c`).

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_16.c`, `0x8006B814` | `$s5` | `addu $s5, $v0` at `0x8006B764` after `jal load_asset` `0x8006B75C` | sole free; matching allocator return |

`$s5` is assigned once. The other `r21` operations in the function
are the callee-save spill at entry, the copy into `$s1` for the
record walk, the delay-slot copy into `$a0`, and the epilogue
restore, which runs after the free. There is no second `jal
rs_free` in the function and no store of `$s5` to a global or
object field.

`load_asset` (`0x8006488C`) is the producer. It calls
`get_asset_size_extra`, `rs_malloc` of that size, copies the
malloc result into `$s2` at `0x800648DC`, DMA-fills that block,
and returns `$s2` via `addu $v0, $s2` at `0x80064914`. The name
argument is `pl_crafts/shadows_TM` at `0x8003C960` (`lui 0x8004`
/ `addiu -0x36A0`). That `addiu` immediate occurs only in this
function. `load_asset`, `full_header_image_offset_convert`, and
`registerHmtTextureInTable` contain zero `jal rs_free`.

The entry halfword test (`lhu` at `0x8013A528 + 2*index`,
`0x8006B748`) returns before `load_asset` when the slot is not
`0xFFFF`, so that path neither allocates nor frees. The back-edges
at `0x8006B7E8` / `0x8006B7F4` / `0x8006B800` / `0x8006B80C` reuse
the same `$s5` with index 9, 10, 11, or 12. They do not call
`load_asset` again. The free is after that chain, once.

The halfword stored at `0x8006B7E0` is `$v0` from
`registerHmtTextureInTable`, not `$s5`. `0x8013A528` is the
texture-id table also written by the closed `hangarLoadShadows`
class. It is not the freed pointer.

## Callers

Three calls, one definition, no overlay duplicate:

| Caller | Site | Argument |
|---|---|---|
| `load_dat_file_assets` | `0x80064A7C` | immediate `13` |
| `load_dat_file_assets` | `0x80064FB4` | `$s1` craft index (`6` or `7` on the two fall-throughs into that call) |
| `allocateAndInitCraftNpcContext` | `0x8006BD54` | incoming `$a2 & 0xF` |

All three pass a craft index. None passes a heap pointer, and none
reads this function's `$s5` (it is restored from the spill slot
before return). `allocateAndInitCraftNpcContext` afterwards reads
the texture-id halfword at `0x8013A528 + 2*index`.

## Host guards already present

Two s613 checks in this function jump to the epilogue at
`0x8006B81C` and therefore skip the free: the `load_asset` return
range check at `0x8006B764`, and the walk-pointer check at
`0x8006B780`. They are pre-existing. This audit does not add,
relax, or rewrite them. Skipping a free of an out-of-range pointer
is not a new writer of `$s5`.

`rs_free` itself returns on a NULL `$a0` (classified in s3611).
Reaching this free with NULL would already have faulted on the
original `lw` / `lhu` of the asset, unless the host guard had
diverted first. That is the same unproven allocator-failure edge
the earlier load_asset-then-free classes left open. It is not a
second pointer source.

A `registerHmtTextureInTable` result of `0xFFFF` could keep the
index-9..12 back-edge alive and never reach the free. That is a
livelock of one still-owned block, not a free of a non-allocator
pointer.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static scope:
the freed register is only the `load_asset` / `rs_malloc` return,
no callee or caller frees it, and the loop frees it once.
H-NextClassUnevaluable is not selected. Runtime allocator and
freelist legitimacy remain unproven. No guard was added.

The next unaudited `jal rs_free` named by the same s3620 leftover
list is `load_naboo_starfighter` at `0x8006C8C4` (`$a0 = $s2`).
The `jal rs_free` census is not exhausted; funcs_16 and above still
hold sites this method has not classified.
