# NEXT work unit — extend the downstream state/output boundary

HYPOTHESIS-ID: m5-downstream-output-state

Session 3477 found that the enumerated early `rs_free` stores do not mutate the
consumer's `s1`: 0/512 joins matched exactly or within `0x100`. Do not repeat
that bounded store set unchanged; later PCs were hidden by the 2048-row cap.

Competing hypotheses and discriminating outcomes:

- `H-LateGuestWriter`: a later `rs_free` store or the `0x80033410`
  return/callee path is the first state/output mutation and joins the
  consumer tuple.
- `H-HostContract`: no guest mutation explains the divergence, while the
  host callback/task/output boundary changes the observed state.
- `H-ObservationInvalid`: controls or entry rows fail; no conclusion is
  allowed without same-run positive controls.

Discriminating measurement: keep the regeneration-safe store table, raise its
budget only for the six later PCs, and add the `0x80033410` return/callee plus
host task/output boundary to the same title-gated table. Each row contains
mutation PC, destination/field, value, caller identity, ordinal, and the next
consumer tuple. Keep the four-PC positive control and run one image arm only.

Before building, inspect the generated path and ask the retail oracle first
with whole-RDRAM control plus the selected mutation PCs and destination
watches. Then batch all port hooks in one build and run from `build/` using
the validated LLE/spin-yield route from Session 3476.

Expected outcomes: an exact late mutation/value-to-consumer match selects
`H-LateGuestWriter`; live controls and consumer rows with no guest mutation
through the host boundary select `H-HostContract`; missing controls or entries are
`H-ObservationInvalid` and require redesign.
