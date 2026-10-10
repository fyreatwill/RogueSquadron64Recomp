# M3 s4478 — load_naboo_starfighter rs_free of the koelsch HMT

## Work unit

Static census of the one original `jal rs_free` in
`load_naboo_starfighter` (`0x8006C780`), at `0x8006C8C4`, which
forwards `$s2` in the delay slot. No build or runtime run was
performed.

The discriminator was that one site plus every original assignment
of `$s2` inside the function, every callee that could free the
same pointer, and every caller that could supply it:

- H-NextClassGap: the free can receive a pointer that is not the
  matching `rs_malloc` return, or can free it again after a
  sibling already released it.
- H-NextClassComplete: the only freed value is that allocator
  return, freed once, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, so the writer cannot be named.

Same-scan positive control: the `jal 0x80001C98` comment pattern
that locates `0x8006C8C4` in `funcs_16.c` also locates the already
closed sites `0x8006B814` (`loadCraftShadowTextures`, s4477) and
`0x80005268` (`rs_zcfree`, s3790, `funcs_1.c`). The ROM word for
that jal is `0x0C000726`. It matches both `0x8006B814` and
`0x8006C8C4`. The cart mapping that reads `pl_crafts/shadows_TM`
at `0x8003C960` reads `pl_crafts/koelsch_HMT` at `0x8003C9B0`.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_16.c`, `0x8006C8C4` | `$s2` | `addu $s2, $v0` at `0x8006C7DC` after `jal rs_malloc` `0x8006C7C0` | sole free; matching allocator return |

`$s2` is written three times in the ROM function. The generated
listing has the same three `r18` assignments.

| PC | Instruction | Reaches the free? |
|---|---|---|
| `0x8006C790` | `lui $s2, 0x8013` | no; overwritten before any branch |
| `0x8006C7DC` | `addu $s2, $v0, $zero` | yes; this is the freed value |
| `0x8006C8DC` | `lw $s2, 0x20($sp)` | no; epilogue, after `jal rs_free` |

There is no branch between `0x8006C790` and `0x8006C7DC`. `$v0`
at the second write is the `rs_malloc` return. The instructions
in between (`0x8006C7C8` through `0x8006C7D8`) write `$a1`, `$s1`,
`$a3`, `$a0`, and `$a2` only. The `lui` value is the base for
`lw $a2, 0x7CFC($s2)` and is dead once `$s2` is rebound.

The `beql` at `0x8006C8BC` compares the sanity-check count with
`$t0`. Its delay slot is `addu $s0, $s4, $zero`, and only on the
taken path. It does not write `$s2`. The record walk
(`0x8006C85C`..`0x8006C8B4`) reads `$s2` as the block base and
does not assign it. Every early-fail delay slot writes `$s0`,
`$v0`, or `$a2`, then branches to the same free. The back-edge
returns to `0x8006C85C`, not to the free. The function has no
`jr` before `0x8006C8C4`.

`rs_malloc` (`0x80001ACC`) is the producer. Its own calls are
`osRecvMesg`, `ensureHeapInitialized`, and `osSendMesg`. It does
not `jal rs_free` and does not `jalr`. The block does not exist
until that call returns.

## What the block is

`get_asset_size_extra` (`0x80004D5C`) is called first, with
`$a1 = 0x8003C9B0` (`lui $s0, 0x8004` / `addiu $s0, $s0, -0x3650`).
That address is the ROM string `pl_crafts/koelsch_HMT`. `$s3`
holds the returned size. `rs_malloc($s3, 0)` then produces `$s2`.

`findAssetAcrossSegments` does not receive this pointer. Its
`$a0`..`$a3` are set while `$s2` is still `0x80130000`, and the
stack argument is zero. It saves the incoming `$s2` at
`0x80004AC0`, rebinds its own `$s2` to `$a3` (the name), and
restores the caller's `$s2` at `0x80004C5C`.

`setupAssetDma` copies the block from the stack argument
`0x14($sp)` into the DMA record at `0x24($a2)`. Its calls are
`sendServiceMessage`, `recvServiceMessage`,
`postMessageToServiceWorker`, `yieldThreadRet1`, and
`getServiceMessagePayload`. None is `rs_free`.
`teardownAssetDma` posts a service message and waits for reply
`0x80FF`. It does not load `0x24` of the record and does not
`jal rs_free`. `decrypt_ns_hmt` (`0x8006AFC0`) XORs the block in
place, has no calls, and does not store the pointer.

Those four callees, plus `get_asset_size_extra` and `rs_malloc`,
contain zero `jalr`. This is not the koelsch path classified in
s3630. That loader decrypts a different malloc around
`0x800567xx` and frees it at `0x80056798`. It does not call
`load_naboo_starfighter`.

The checks after decrypt (`word at +4` against the size, 4-byte
alignment, count `< 0x29`, then a `0x34`-stride walk) decide
whether `$s0` becomes the caller argument or stays zero. They
do not choose a different block. `lw $a1, 4($s2)` at `0x8006C824`
runs on every path before the free. A NULL malloc faults there
on the original instruction stream. The generated function has
no range check that skips the load or the free. The store probes
on the callee-save spills do not assign `$s2`.

## Callers

One definition. One generated call. One uncompressed-ROM hit of
the jal word `0x0C01B1E0`, at file offset `0x82EE0`, which is
VRAM `0x800822E0`.

| Caller | Site | Argument |
|---|---|---|
| `applyCheatCodeFromInput` | `0x800822E0` | `$v0` from `rs_crc32` of 8 bytes at the caller's `$s0` |

The call runs only when bit `0x10` of `*(0x80130B58)` is set.
`0x80130B58` is the cheat-flag word. The delay slot stores
`flags & ~0x10` back to that word. It does not write `$a0`.
`$a0` was set at `0x800822CC` from the CRC and is not written
again before the jal. The callee saves it in `$s4` and returns
it only when the `beql` is taken; otherwise it returns zero.
The return is stored at `0x80130B68`. Neither the argument nor
the return is the malloc block, and the caller does not read
this function's `$s2` (the epilogue restores it before `jr`).

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static scope:
the freed register is only the `rs_malloc` return, no callee or
caller frees it, and the function frees it once.
H-NextClassUnevaluable is not selected. Runtime allocator and
freelist legitimacy remain unproven. No guard was added.

`funcs_16.c` has four `jal rs_free` sites. `0x8006B814` was
closed in s4477, and `0x8006C4A8` / `0x8006C650`
(`splineWalkerCraftNpcHandler`, `stubNpcHandler`) were closed in
s3620. This was the last unclassified site in that file.

The next unaudited `jal rs_free` in address order is
`runIdleFramesAndLoadSaveData` at `0x8006DA28` (`$a0 = $s0`,
entry `0x8006D900`). s3653 and s3656 name that function only as
a caller of `initSaveData` and `findManifestEntryByName`. They
do not classify `0x8006DA28`. `$s0` is a loop counter earlier in
the function and is rebound from `$v0` at `0x8006DA00`, before
`initSaveData` and before this free. Do not treat the counter
as the freed pointer without showing that the rebind does not
dominate, and do not re-audit `initSaveData`.
