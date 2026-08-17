# M4 accumulator ground-truth measurement

Preparation result for the next M4 measurement. The retail oracle is an
independent CPU/RDRAM witness, not an RSP register witness: its write watches
can attribute RDRAM writers and its VI trace can prove phase reachability, but
the internal RSP `ACCH:ACCM:ACCL` tuple is not memory-mapped and cannot be
watched there.

## What the oracle can discriminate

The oracle run must carry both controls in the same invocation:

1. `--watch-write 0x0:0x800000` as the whole-RDRAM positive control. A zero
   whole-RDRAM count invalidates every targeted null.
2. A targeted watch covering the retail shaded-emitter input/output record
   addresses, selected only after the port-side probe identifies the stable
   physical range. `--vi-trace` (and the verified input schedule if needed)
   must show the corresponding shaded phase, not merely boot or attract.

The targeted result has three interpretations:

- A retail PC writes the candidate input/output record during the reached
  phase: the game owns that RDRAM edge, so a port-side mismatch cannot be
  assigned to an invented source without explaining the divergence.
- The whole-RDRAM control passes, the shaded phase is reached, and the
  targeted watch stays quiet: the candidate address/range is not a retail
  writer and the proposed source is rejected.
- The whole-RDRAM control passes but the shaded phase is not reached: the
  targeted null is unevaluable, not evidence for a runtime-only origin.

The oracle cannot select saturation versus ordinary arithmetic by itself. That
selection requires the port capture below, with the oracle serving as the
independent reachability and RDRAM-ownership line.

## Smallest complete paired capture

One future port build/run should emit, phase-gated to the first positive
`L_16B8` calls and with a bounded sample budget, one row containing:

`phase, task, ucode overlay, r9, v4[4], v0[4], ACCH[4], ACCM[4], ACCL[4],
v6_pre[4], v6_post_vmadh[4], v6_post_vge[4], output_record[0x18..0x4f]`.

The positive control is an independent non-M4 RSP arithmetic site in the same
run whose accumulator probe must fire with a nonzero or changing tuple. A
counter at `L_16B8` alone is not a control. The M4 row must be taken at the
exact final `VMADH v6,v4,v0`, before the following `VGE`, and again immediately
after it; the output record confirms the store destination and its resulting
bytes.

The comparison is deterministic:

- `v6_post_vmadh` matches the local VMADH model from the captured tuple, but
  `v6_post_vge`/stored bytes differ: VGE or store semantics remain open.
- The VMADH result already differs from the model: accumulator/product
  arithmetic or operand lanes are the active defect.
- The port tuple and store agree, while the oracle attributes a different
  retail record writer/input transition: source-state or execution divergence
  is active; do not add an RT64 mitigation.

No result is admissible without both the port positive-control row and an
oracle whole-RDRAM positive control. The oracle target range must be derived
from the same port capture; hard-coding an address before that capture would
make a null indistinguishable from watching the wrong record.

## s1512 close of the parked `0x688:0x710` remainder

s1135 treated captured `r9=0x670..0x6C0` as RDRAM and parked a CPU write
watch on physical `0x688:0x710`. Dummy-video arms never reached the shaded
phase. The s1512 Rice hangar recipe reached 512 / origin `0x006ab400` with
the whole-RDRAM control passing (10000 callbacks, removal rc=0), 11 Start
injections with matching PIF `7C4=0x10000000`, and both
`0x688:0x710` and SP-DMEM `0x04000670:0x04000720` at zero CPU writes.
Generated overlay 0x20 sets `ori $9, $zero, 0x670` and the only `SP_WR_LEN`
site DMAs DMEM `0xD60`, not `0x670`. Do not re-watch `0x688:0x710`. A new
M4 oracle target needs a real RDRAM destination, not the DMEM record base.
The oracle still cannot see `ACCH:ACCM:ACCL`.

## s1602 paired result

The corrected LLE-solo port run passed the independent stage-1 arithmetic
control and captured four phase-6 target rows. The exact local VMADH model
matched all 32 target lanes, and post-VGE values were unchanged. This closes
the local VMADH/VGE mismatch hypotheses for the captured path as a
single-source runtime consistency result, not an independent retail arithmetic
proof.

The port's live shade-DMA control identified `0x4B7800..0x4B7808` as a real
runtime destination, while the probe `r9=0x670/0x6C0` values remained DMEM.
The retail Rice oracle passed its whole-RDRAM positive control and reached
the 512 hangar, but wrote the port candidate zero times. Because the port
destination is runtime-allocated and the port/oracle scene origins differ,
that targeted null is single-source and does not establish retail ownership
or source-state divergence. A future M4 oracle target still needs a stable
cross-runtime address or an independently attributed writer identity.

## s1824 overlay-0x20 consumer table

Static classification of every live `0x670` / `0xD60` / `SP_WR_LEN` /
`SP_RD_LEN` site in `build/factor5_ucode/factor5_ucode_ovl20_recompiled.c`.
No new runtime field. The open split was whether the `L_1740` `v6` bytes
leave DMEM `0x670` into the only write-DMA staging buffer (`0xD60`).

Vertex records are 0x28 bytes; `L_1740` writes a pair per iteration
(`r9 += 0x50`). `+0x40($base)` is `+0x18` of the second vertex
(`base+0x28`). `sdv v6[0], 0x18($9)` covers `+0x18..+0x1F`; the
immediately following `ssv v7[4], 0x1E($9)` overwrites the last
halfword, so live `v6` bytes are `+0x18..+0x1D` (and `+0x40..+0x45`
on the pair). Color is a different field: lighting `sw`/`slv` at
`+0x10`/`+0x14`, later `luv` in `L_17F0`. GLideN64's `F3DSWRS_Tri`
indexes vertices as `/ 40` and sources color from
`gSP.vertexColorBase + index`, not from a vertex `+0x18` field.

| Site | Kind | Classification |
|---|---|---|
| `ori $9, $zero, 0x670` :1078 | producer base | `L_162C`/`L_1740` store of `v6` to `r9` |
| `addiu $11, $11, 0x670` :619/630 | index addend | builds `r11/r12/r13` into the table; writes `+0x10`/`+0x14` (color). Does not load `+0x18`/`+0x40` |
| `addiu $15, $15, 0x670` :803/806 | index addend | same write-only color poke at `+0x10`/`+0x14` |
| `L_17F0` `llv`/`lh`/`lsv` `0x18($11/$12/$13)` :1386–1579 | post-store reader | loads the stored `v6` XY; `ssv` of Y to `0x2/0x4/0x6($16)` and scaled X to `0x8/0xA($16)` |
| `L_17F0` `lsv` `0x1C($11/$12/$13)` :1826–1834 | post-store reader | remaining `v6` halfword 2 into later RDP attribs |
| `L_17F0` `luv` `0x10($11/$12/$13)` | color, not `v6` | lighting-written RGBA |
| no `0x40($11/$12/$13)` load | pair alias | second-vertex `v6` is `0x18($base+0x28)` |
| `jal 0x11FC; ori $2, $zero, 0xD60` :224–228 | DMA write | the only `SP_WR_LEN` call; `SET_DMA_MEM(r2)` with `r2=0xD60` |
| `SP_RD_LEN` :281, :378 | DMA read | DMEM `0x170` / generic `r3`; not `0x670` |
| `ori $16, $zero, 0xD60` :240, :2265, :2269, :2287 | write-pointer reset | unrelated addend |
| `sdv`/`ssv` `0x18($16)` / `0x18($29)` | dest is D60/scratch | computed RDP coefficients, not a `0x670` load |

Every sibling overlay (`ovl4/10/12/14/18/1c/24`) has the same single
`jal 0x11FC; ori $2, $zero, 0xD60` write-DMA. None sources `SP_WR_LEN`
from `0x670`.

`L_17F0` is the restage: `sb $10, 0x0($16)` stores `*(u8*)(state+0x37) | 0xC8`
(RDP triangle command) at the `r16` cursor, which is initialized to
`0xD60` and flushed by `L_112C` when `r16 - 0xD60 != 0`. The loaded
`+0x18` halfwords become that command's Y and X, not a raw 8-byte memcpy.

Verdict: **H-rdp-consumer selected.** H-later-dma-raw is refuted (live
`SP_WR_LEN` source is only `0xD60`). H-dead-store is refuted (`L_17F0`
reads `+0x18`/`+0x1C`). H-source-state as "no generated path copies the
stored bytes into `0xD60`" is refuted by the XY restage. The stored
`0xFFFF8000`/`0x00008000` sentinel, if still present at `+0x18` after
`L_1740`, is the RDP triangle X/Y payload. Next M4 measurement is that
command's shape in the `0xD60` buffer (header `0xC8`, YH/YM/YL/XL), not
another DMEM or runtime-allocated RDRAM watch.
