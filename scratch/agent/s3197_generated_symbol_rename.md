# Session 3197 — generated symbol classification at `0x800A2924`

The bounded companion census found no `0x800A2924` semantic symbol. The
generated record begins with an isolated `srl` and continues with
data-decoded/invalid instructions and trap-like stores; it has no standalone
callable prologue or generated callsite. This selects `H-DataGap` and rules
out `H-SemanticMatch` and `H-Ambiguous` for this record.

The regeneration-safe mapping helper was extended with
`static_3_800A2924` → `data_gap_800A2924`. Running the helper synchronized
exactly three external generated references in `funcs_49.c`, `funcs.h`, and
`recomp_overlays.inl`; a final search found no stale old-name reference.
No build or runtime run was needed; the change is source-only.
