# NEXT: close the full-grid writer/source boundary
HYPOTHESIS-ID: g1c-span-grid-writer

Run exactly one bounded experiment. Extend the keyed probe to include all
seven known span-table writer sites and a first-call full-grid baseline, then
log the per-cell filter input and selected span bytes for the same dd1 nonempty
and dd4 EMPTY keyed controls. Do not add a guard or change game behavior.

Competing hypotheses and discriminator:

- H-raster-grid: the first baseline and known writers explain the full grid;
  dd4 empty returns are a legitimate rasterizer/input result.
- H-uninstrumented-init: an uninstrumented initializer or writer supplies the
  bytes used by the dd4 filters.
- H-late-writer: a known writer changes the sampled rows after rasterization.

The discriminating measurement is the keyed first-baseline-to-return diff,
with all seven writer PCs and per-cell filter inputs joined to the same stream
return. A null is invalid unless the full-grid initialization control visibly
fires in the same run.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    python3 tools/apply_s6512_span_writers.py
    zsh scratch/agent/s6512_span_writers.sh
