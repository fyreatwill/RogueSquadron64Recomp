# NEXT: resume the span-filter decision join
HYPOTHESIS-ID: g1c-span-grid-writer

RESUME: the s6513 experiment was not run during checkpoint close-out. Run
exactly one bounded experiment. Add a phase-gated, rate-limited trace at
the per-cell span filter in `streamTerrainGridCellsByDistance` containing the
cell row/column, window words, selected signed span bytes, and the current
eight-site writer sequence; join it to the existing keyed return snapshot.
Keep the `[span-base]` positive control and run the pinned dd1/dd4 arms in one
Debug build. Do not add a guard or change game behavior.

Competing hypotheses and discriminator:

- H-filter-legitimate: dd4 EMPTY cells read all-127 spans before any later
  rewrite.
- H-late-rewrite: the filter reads populated spans, then DB4/DC0 rewrites the
  grid before the keyed return snapshot.
- H-missing-source: the filter reads a non-127 value written by a site absent
  from the eight-PC census.

The discriminating measurement is the per-cell decision value joined to the
same keyed return. A null is invalid unless `[span-base]` fires in both arms.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    python3 tools/apply_s6513_span_filter.py
    zsh scratch/agent/s6513_span_filter.sh
