# NEXT work unit — re-qualify the downstream capture route

HYPOTHESIS-ID: m5-downstream-output-state

Session 3478 built the post-call `osSendMesg` and host task/output witnesses,
but all three port route attempts stopped in the 640 phase. Do not interpret
their zero title rows; first reproduce the known title-reaching image route.

Competing hypotheses and discriminating outcomes:

- `H-LateGuestWriter`: a later `rs_free` store or the `0x80033410`
  return/callee path is the first state/output mutation and joins the
  consumer tuple.
- `H-HostContract`: no guest mutation explains the divergence, while the
  host callback/task/output boundary changes the observed state.
- `H-ObservationInvalid`: controls or entry rows fail; no conclusion is
  allowed without same-run positive controls.

Discriminating measurement: use the exact title-reaching image-arm command
from the retained s3477 run, first with the existing four-PC positive control.
If title is reached, use the same built binary with the six later PCs plus
the `0x80033410` return/callee and host task/output rows. Do not interpret
nulls without title and control rows.

Before building, inspect the generated path and ask the retail oracle first
with whole-RDRAM control plus the selected mutation PCs and destination
watches. Then batch all port hooks in one build and run from `build/` using
the validated LLE/spin-yield route from Session 3476.

Expected outcomes: title/control live then an exact late mutation/value match
selects `H-LateGuestWriter`; title/control live with no guest mutation through
the host boundary selects `H-HostContract`; missing title or controls select
`H-ObservationInvalid` and require route repair.
