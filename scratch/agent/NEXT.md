# NEXT work unit — M5 selector-table writer boundary

HYPOTHESIS-ID: m5-selector-table-writer-boundary

Session 3507 disabled audio on the same forced-LLE/no-spin route. It also
stopped at VI 640 with live controls and no crash, so selector rows must now
be collected on the already-qualified real-image/LLE/spin-yield route.

Competing hypotheses and discriminating measurement:

- `H-TableWriterParity`: retail and port table writes match at the first
  common title-origin/index/address/value boundary, closing this edge.
- `H-TableWriterDivergence`: the first ordered table write differs, selecting
  its writer/initializer or selector-index producer as the next edge.
- `H-TableRouteAbsence`: a candidate writer is live in retail but absent in
  port while both positive controls fire, selecting a route difference.
- `H-CaptureInvalid`: the retail whole-RDRAM or port title/pre-call control is
  absent, making the table comparison unevaluable rather than null.

Discriminating measurement: first run the independent retail preflight with
the whole-RDRAM positive control, title phase, and watches for the
`0x8009131C` predecessor/table-selection range. In the same build, run the
qualified real-image/LLE/spin-yield port arm with the existing pre-call,
caller, producer, and selector controls plus a bounded table-write witness.
Join by title origin, table address, stored value, selector index, and caller
arguments; the first matching or differing write selects the boundary. A
missing control makes the result unevaluable.

Use the existing Session 3501 selector-load instrumentation and its validated
real-image/LLE/spin-yield/autopilot recipe as the route template; capture to a
non-dot final path under `scratch/agent/` and SIGKILL any watchdog survivor.
Do not interpret pre-title nulls from the silent/no-spin arm as table-writer
evidence.
