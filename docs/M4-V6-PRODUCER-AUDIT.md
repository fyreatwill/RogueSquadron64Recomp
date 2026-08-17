# Factor 5 `v6` producer audit

The `L_16B8` path does not source shade from the per-vertex color record.
This is a static audit of the generated Factor 5 ucode, cross-checked against
the captured ucode-data image.

## Mode and control flow

At `factor5_ucode_ovl1c_recompiled.c` lines 1035–1039, the mode is loaded as
`r3 = DMEM[0x134] & 1` (`DMEM[0x34]` relative to the state base `r18=0x100`).
The call at `L_162C` enters `L_179C` and returns to `L_16B8` with `r3` intact.
At `L_16B8`, both arms execute the same final `vge` and then fall through to
`L_1740`; the nonzero arm only applies additional `v3`-based adjustments to
`v4`/`v5` before the store.

## Complete `v6` dataflow

1. `vge v6, v27, v30[0]`, followed by `vmrg v6, v27, v31[0]`, creates an
   intermediate compare/select result. It is consumed immediately by the
   `v5`/`v4` multiply-accumulate sequence.
2. `vmadh v6, v4, v0` overwrites that intermediate result on both mode paths.
3. The mode-zero delay/branch arm executes `vge v6, v6, v29[1q]`; the
   nonzero arm executes the same `vge` in its branch delay slot before doing
   its extra `v3` adjustment. Thus the final `v6` stored at `L_1740` is the
   same compare result in either mode.
4. `sdv v6[0], 0x18($9)` and `sdv v6[8], 0x40($9)` write the final vector to
   the output record. There is no load from record `+0x10` or from the
   VTXCOLOR array in this path.

The producer is therefore a transformed-vector/compare path, not a clip-only
register copy: it contains vector arithmetic (`vmadh v6,v4,v0`) followed by a
`vge` against the threshold vector. However, it is also not a color or
lighting-source load. The generated path has no operation that can inject the
vertex RGBA bytes into this shade vector.

## DMEM `0x60` source

The two `ldv` operations at `L_16B8` load the 16-byte vector at DMEM `0x60`
into `v29`. In the captured ucode-data image (`build/ucode_099FE0.bin`, file
offset `0xAE80`, corresponding to runtime ucode-data address `0xA4E00+0x60`),
the bytes decode as signed halfwords:

`0577 638F 1756 FF96 04D1 62CB 18CB FF8A`

This is a varying signed lookup/table vector (the surrounding bytes continue
the same table), not four RGBA channels and not a lighting constant block.
The `vge` compares the computed `v6` against one lane of this table-derived
vector; it does not turn the table into color.

## Verdict

`H-v6-mode-misread` is refuted: the mode bit and both control-flow arms are
unambiguous, and both reach the same shade store. `H-v6-lighting-result` is
also not supported: the source is transformed-vector arithmetic plus a table
threshold, with no lighting/color load. The remaining result is
`H-v6-clip-predicate` in the narrow sense that the final `vge` is a
predicate-like compare, while its input is transformed-vector arithmetic
rather than a standalone clip mask. This refines, but does not yet explain,
why the compare produces the observed `-0.5/+0.5` sentinel. s1824's
consumer table (`docs/M4-ACCUMULATOR-GROUND-TRUTH.md`) shows those
stored bytes are restaged as RDP triangle X/Y, not as shade. No
mitigation or runtime change is authorized.
