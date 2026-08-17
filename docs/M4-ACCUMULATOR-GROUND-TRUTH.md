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
`L_1740`, is the RDP triangle X/Y payload. Command *shape* is closed
by s1840 below; do not re-walk this consumer table.

## s1840 restaged RDP command shape

Mandatory 15-title M4 REVISIT. No new runtime field. Discriminator is
whether every `L_17F0` store into the `r16` / `0xD60` cursor matches
the official RDP Fill Triangle base (n64brew `0x08`–`0x0F`; first
stored byte `0xC8 | flags`) or some other layout.

Two independent sources: generated ovl20 `L_17F0` (sibling overlays
share the same restage) and the n64brew triangle command plus RT64's
decoder at `lib/rt64/src/gbi/rt64_gbi_rdp.cpp:376-400`. GLideN64
`F5Rogue.cpp` is HLE (`gSP1Triangle`) and does not emit this RDP
command, so it is not a second source for the on-the-wire shape.

Y-sort before the stores: `lh` of `+0x1A` on the three vertices,
3-bit compare index, permute via DMEM `0xAA`/`0xB1`/`0xB8`, then
`llv` XY from the permuted pointers into `v15`/`v14`/`v13`. `lmajor`
is `mfc2 v29[5] & 0x80` ORed with `*(u8*)(state+0x3A)` (level/tile).

| Cursor off | Store | Official field (n64brew / RT64) |
|---|---|---|
| `+0x00` | `sb r10`; `r10 = *(s8*)(state+0x37) \| 0xC8` | bits 63:56 command. `0xC8` is `G_RDP_TRI_FILL`; bit2 shade, bit1 texture, bit0 z |
| `+0x01` | `sb r14`; `r14 = (r14 & 0x80) \| *(u8*)(state+0x3A)` | bit55 `lmajor`, bits 53:48 level/tile |
| `+0x02` | `ssv v15[2]` (Y of sorted `$13`, vertex `+0x1A`) | bits 47:32 **YL** (s11.2). s1824's "YH at +2" was store-order, not the spec name |
| `+0x04` | `ssv v14[2]` (Y of sorted `$12`) | bits 31:16 **YM** |
| `+0x06` | `ssv v13[2]` (Y of sorted `$11`) | bits 15:0 **YH** |
| `+0x08` / `+0x0A` | `ssv v12[0]` / `ssv v13[0]` after `lsv 0x18($12)` + `vmudm v30[4]` | word1 **XL** s16.16. Source is the 16-bit X at vertex `+0x18`, not a 32-bit memcpy of `0xFFFF8000` |
| `+0x0C` / `+0x0E` | `ssv v0[2]` / `ssv v1[2]` (reciprocal of Y-delta) | word1 **DxLDy** |
| `+0x10` / `+0x12` | `ssv v9[8]` / `ssv v3[8]` | word2 **XH** |
| `+0x14` / `+0x16` | `ssv v0[10]` / `ssv v1[10]` | word2 **DxHDy** |
| `+0x18` / `+0x1A` | `ssv v9[4]` / `ssv v3[4]` | word3 **XM** |
| `+0x1C` / `+0x1E` | `ssv v0[6]` / `ssv v1[6]` | word3 **DxMDy** |

Then `addi $16, $16, 0x20`. If header bit1 (texture) is set, a 64-byte
tex suffix is written (`sdv` at `+0x08/+0x18/+0x28/+0x38/+0x20/+0x30`
relative to the advanced cursor). If bit2 (shade) is set, `addi $16,
$16, 0x40` and the shade coefficient block is stored. `L_112C` flushes
when `r16 - 0xD60 != 0` via the only `jal 0x11FC; ori $2, 0xD60`
`SP_WR_LEN`.

Sentinel split (static): `sdv v6[0], 0x18($9)` of `0xFFFF8000` /
`0x00008000` is two 16-bit fields, not one s15.16 X. `+0x18 = 0xFFFF`
is the X halfword that is scaled into XL; `+0x1A = 0x8000` is the Y
halfword written raw into YL/YM/YH. RDP Y uses bits 13:0 as s11.2, so
`0x8000` is `0.00` on the hardware field (RT64's `<<2>>2` on the full
16-bit value sign-extends to −8192). Three equal Ys are a zero-height
command. Clip flags at vertex `+0x24` (written just before `L_16B8`)
can reject the triangle at `L_17F0` entry (`0x7070` all-out →
`L_1DA8`; `0x4343` partial → `L_1268`) before any `0xD60` store.

Verdict: **H-standard-edge selected.** H-y-swapped is refuted (offset
`+2` is official YL, matching RT64 `w0 & 0xFFFF`). H-s1516-passthrough
is refuted (`lsv` of two bytes at `+0x18`, then `vmudm`). H-not-triangle
is refuted (`0xC8` plus the 32-byte edge block plus optional shade/tex
suffixes). No mitigation. Do not re-watch `0x688:0x710`, recapture
VMADH/VGE, watch `0x4B7800`, or re-enumerate the ovl20 consumer table.

Parked M4 remainder is no longer the command *shape*. It is whether a
live `0x8000` Y is clip-rejected, emitted as a zero-height command, or
emitted with an on-screen Y — that needs a phase-gated dump of a
`0xD60` command whose YL/YM/YH halfwords are `0x8000`, not another
static walk.

## s1856 live `0x8000` Y at L_17F0 / L_112C

Mandatory 15-title M4 REVISIT. One build, one LLE-solo run, counters
in `tools/fixup_factor5_ucode.py` fixup 20 plus host
`rs64_m4_y8000_*` in `src/rsp/dpc_bridge.cpp`. Phase-gated to VI 640
(`ROGUESQ_M4_Y8000_WIDTH=640`). Attribution-page LLE only
(`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_SOLO=1`, no `UNGATED`). Log:
`scratch/agent/s1856_m4_y8000_lle/run.log`. A prior HLE-only arm
(`scratch/agent/s1856_m4_y8000/run.log`) printed zero `[m4-y8000]`
lines — L_17F0 is LLE-only; that arm is the same-run reminder that
HLE is not a witness.

Same-run positive controls:

- `[lle-force]` plus `[lle send_dl #1..#256]` `gate=attr exit=1`
- `[m4-y8000] mark flush-site phase=2 viw=320 r16=0xD68`
- `[m4-y8000] mark entry phase=4 viw=640 y=05C6/05CA/05C4 clip=0000/0000/0000`
- last summary: `entry=15921 flush=542336 hdr=9229`

| Counter (VI 640) | Value |
|---|---|
| `n_entry` | 15921 |
| `n_y8000_entry` | 0 |
| `n_entry_allout` / `partial` / `fall` | 0 / 0 / 0 |
| `n_flush` / `n_empty` / `n_hdr` | 542336 / 6692 / 9229 |
| `n_y8000_any` / `equal` / `mixed` | 0 / 0 / 0 |

H-clip-reject needs `n_y8000_entry > 0`. H-zero-height-emit needs
`n_y8000_equal > 0`. H-on-screen-emit needs `n_y8000_mixed > 0`.
All three stay at zero. H-never-live (`n_flush > 0` and
`n_y8000_entry == 0`) is selected for this window.

Single-source: one port LLE attribution-640 capture. The two sites
(L_17F0 Y load vs flushed YL/YM/YH) corroborate each other but are
not an oracle line. 128 non-attribution DLs were HLE-bypassed
(`[lle send_dl skip]`). The s1602 sentinel was hangar-shaped; this
window does not close a hangar/512 check. Do not re-walk the command
shape or the ovl20 consumer table.

## s1872 hangar/512 live `0x8000` Y — UNEVALUABLE

Mandatory 15-title M4 REVISIT. Hangar-origin gate on the s1856
counters (`ROGUESQ_M4_Y8000_WIDTH=512` plus `rs64_is_hangar_vi`
for origins `0x006ab400` / `0x006ab800`). Four port arms, all
stuck in the `640→2→640` lifecycle at origin `0x00696100`:

| Arm | Log | Result |
|---|---|---|
| Attribution LLE + boot Starts | `scratch/agent/s1872_m4_y8000_hangar512/run_attr_lle.log` | Controls fired (gate=attr, mark flush-site/entry, hangar=0). Gated `n_flush=0`. No 512/1024. |
| Hangar-only LLE + boot Starts | `scratch/agent/s1872_m4_y8000_hangar512/hangar_only/run.log` | `[lle-force]` only. Still 640 at 136s. |
| Hangar-only LLE, wait 1024 | `scratch/agent/s1872_m4_y8000_hangar512/from1024/run.log` | Same 640 lifecycle. |
| HLE, wait 180s for 1024 | `scratch/agent/s1872_m4_y8000_hangar512/hle_to_hangar/run.log` | probe exit 5; last width 640. |

Zero hangar-origin marks, zero `gate=hangar`, zero attract 512.
This selects UNEVALUABLE and does not select any H-*. Re-open
only after a port `[phase] vi_width=512 origin=0x006AB400`.
Do not treat 640 gated zeros as hangar.
