# NEXT work unit (s1009)

s1008 (offline static audit): the generated Factor 5 path loads four unsigned
color bytes and copies them to each transformed vertex at `+0x10`. The shaded
triangle path later reads vertex data at `+0x18` and emits shade halfwords from
geometry/vector registers; no read of `+0x10` occurs before those stores. The
only `lb` in the region (`0x37($18)`) feeds packed flags, not shade. The
independent GLideN64 reference copies `colorData` directly to vertex RGBA.
`H-shade-source-mismatch` is selected; no mitigation was made.

HYPOTHESIS-ID: m4-zero-shade-emission-constant

## One work unit

Trace the color-bearing vertex record from the Factor 5 ELF/disassembly through
`tools/fixup_factor5_ucode.py` and RSPRecomp generation. Determine whether the
missing shaded-triangle read of vertex `+0x10` is present in the original
microcode or was lost by the generated/fixup pipeline. Static audit only; do
not build, run, or edit generated output.

Competing hypotheses and discriminating measurement:

- `H-original-omits-color`: the retail microcode itself never consumes the
  color word for shaded-triangle emission.
- `H-generation-drops-color`: the original microcode has a color read, but
  disassembly conversion, RSPRecomp, or fixup omitted it.
- `H-layout-misread`: a generated color read feeds the vectors, but RT64 reads
  the wrong record offsets.

Discriminator: compare the original ELF instruction sequence and the generated
sequence around the vertex-record color store and shaded-triangle entry. A
color read absent in both selects `H-original-omits-color`; present only in the
ELF selects `H-generation-drops-color`; present in generated code and feeding
shade vectors with an offset discrepancy selects `H-layout-misread`. Record the
exact producer/consumer instruction pair before proposing any fix.

The `slotDispatcherIter` sp-guard soak remains queued separately in
`scratch/agent/soak_queue/slot_sp_guard.sh`.
