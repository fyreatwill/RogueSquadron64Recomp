# Session 3073 generated-symbol audit — `0x800C41AC`

## Hypotheses

- H-ExactIdentity: an independent companion source names a callable or
  preamble here.
- H-DataGap: the address is a fragment/data boundary with no independent
  semantic identity.
- H-MappingDrift: companion, generated output, or project metadata disagree
  on address or extent.

## Six-surface comparison

1. Companion mission map: `data_gap_800C41AC = 0x800C41AC`, immediately before
   `plotRadarBlipColumn = 0x800C41B0`.
2. Companion `build/redefs.txt`: all three entries (`func_`, `D_`, and
   `fake_func_800C41AC`) map to `data_gap_800C41AC`; no independent semantic
   name is present.
3. Generated body: `funcs_33.c` emits a 4-byte body containing only
   `add.s $f22, $f0, $f2`; it has no prologue, return sequence, or generated
   caller targeting the placeholder. The preceding generated function also
   contains an instruction at this address, consistent with a boundary
   artifact rather than an independently callable function.
4. Header: `funcs.h` declares `data_gap_800C41AC`.
5. Overlay registration: `recomp_overlays.inl` registers offset `0x1F07C`
   with ROM size `0x4`.
6. Project symbol TOML and rename tooling: both use address `0x800C41AC`,
   size `0x4`, and `data_gap_800C41AC`; the rename tool maps the generated
   fake name to that mechanical name.

## Result

H-DataGap selected. H-ExactIdentity is unsupported because neither companion
surface supplies a semantic identity, and H-MappingDrift is not supported by
the matching address/extent metadata. No rename or build was needed.
