# NEXT work unit — obtain ordered retail source-writer values

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3461 qualified the port title witness again: 1,024 ordered rows (768
at `0x800644B0`, 256 at `0x80064524`), all zero. The independent s3458 retail
artifact has only per-PC totals and value histograms, so the join is
unevaluable until retail emits ordered rows.

Competing hypotheses and discriminating outcomes:

- `H-RetailOrderedParity`: ordered retail rows can be captured and join to the
  existing port rows; the source boundary can be selected.
- `H-RetailHistogramOnly`: the oracle still emits only aggregates; the join
  remains unevaluable and the oracle output path is the defect.
- `H-RetailRouteAbsent`: the retail title phase or named stores are absent;
  the route qualification remains unresolved.

Before any port build, extend the independent oracle's post-store sampler to
emit bounded ordered `(title phase, writer PC, post-store value)` rows, then
run the existing s3458 retail recipe with the whole-RDRAM control and physical
source watch. The discriminator is whether ordered rows are present: rows
that join to the existing port sequence select `H-RetailOrderedParity`; an
aggregate-only output selects `H-RetailHistogramOnly`; absent title/store
rows select `H-RetailRouteAbsent`.
Do not alter audio waits, slots, dispatch, clear behavior, or PCM writeback.
