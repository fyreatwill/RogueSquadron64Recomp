# NEXT work unit — locate the first downstream state/output mutation

HYPOTHESIS-ID: m5-downstream-output-state

Session 3476 found the sole `zcfree` caller-side edge and ruled out an
uninstrumented assignment between `0x80005268` and `rs_free`; do not repeat
that edge join unchanged.

Competing hypotheses and discriminating outcomes:

- `H-DownstreamWriter`: the first state/output divergence is a generated
  store or field mutation after the `zcfree` edge; matching its site/value to
  the consumer selects it.
- `H-HostContract`: no guest mutation explains the divergence, while the
  host callback/task/output boundary changes the observed state.
- `H-ObservationInvalid`: controls or entry rows fail; no conclusion is
  allowed without same-run positive controls.

Discriminating measurement: enumerate generated stores and field mutations
on the path from the sole `zcfree` edge to `0x80001CB8`/`0x80001CC8`; add one
regeneration-safe, title-gated table containing mutation PC,
destination/field, value, caller identity, ordinal, and the next consumer
tuple. Keep the four-PC positive control, and run one image arm only.

Before building, inspect the generated path and ask the retail oracle first
with whole-RDRAM control plus the selected mutation PCs and destination
watches. Then batch all port hooks in one build and run from `build/` using
the validated LLE/spin-yield route from Session 3476.

Expected outcomes: an exact post-edge mutation/value-to-consumer match selects
`H-DownstreamWriter`; live controls and consumer rows with no guest mutation
select `H-HostContract`; missing controls or entries are
`H-ObservationInvalid` and require redesign.
