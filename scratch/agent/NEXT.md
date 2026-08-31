# NEXT work unit — repair regeneration-safe late-store capture

HYPOTHESIS-ID: m5-downstream-output-state

Session 3479 re-qualified the image route. The late-only run reached title and
passed host/post-call controls, but the late-store positive control stayed
zero because the generated `rs_free` path has writer-parity hooks at the six
late PCs rather than the regeneration-safe downstream hook.

Competing hypotheses and discriminating outcomes:

- `H-LateGuestWriter`: a later `rs_free` store or the `0x80033410`
  return/callee path is the first state/output mutation and joins the
  consumer tuple.
- `H-HostContract`: no guest mutation explains the divergence, while the
  host callback/task/output boundary changes the observed state.
- `H-ObservationInvalid`: controls or entry rows fail; no conclusion is
  allowed without same-run positive controls.

Discriminating measurement: update `tools/apply_s3477_m5_downstream.py` (or
the current fixup path) so all six late PCs call the same
`rs64_m5_downstream_store` helper, rebuild, and run the title-reaching image
route with `ROGUESQ_M5_DOWNSTREAM_LATE_ONLY=1`. Title plus the late positive
control and per-PC rows are required. A matching late mutation selects
`H-LateGuestWriter`; title/control with no late mutation through
`0x80033410` selects `H-HostContract`; missing control selects
`H-ObservationInvalid`.

Before building, inspect the generated path and ask the retail oracle first
with whole-RDRAM control plus the selected mutation PCs and destination
watches. Then batch all port hooks in one build and run from `build/` using
the validated LLE/spin-yield route from Session 3476.

Expected outcomes: title/control live then an exact late mutation/value match
selects `H-LateGuestWriter`; title/control live with no guest mutation through
the host boundary selects `H-HostContract`; missing title or controls select
`H-ObservationInvalid` and require route repair.
