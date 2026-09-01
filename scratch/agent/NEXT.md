# NEXT work unit — M5 selector-table writer attribution

HYPOTHESIS-ID: m5-selector-table-writer

Session 3501 selected `H-PreCallState`: retail's post-load `a0` at
`0x80091320` was always `0x801772F0`, while the qualified port alternated
between `0x80175960` from `0x80150000` and `0x801772F0` from `0x80150004`.
The next boundary is the writer/initializer of those table entries or the
selector-index source that chooses them.

Competing hypotheses and discriminating outcomes:

- `H-TableWriterValue`: the same table-entry writer route is live in retail
  and port, but the stored value differs; the first differing post-store value
  selects the producer/value edge.
- `H-TableWriterRoute`: retail and port use different writer PCs or write
  addresses; a route difference selects the missing initialization path.
- `H-IndexSelection`: the table contents match at the relevant entries, but
  the selector index differs before `0x8009131C`; matching writes plus a first
  differing index selects the index producer.
- `H-TableObservationFailure`: positive controls fire but the bounded table
  watch or port writer witness has no rows; repair the observation before
  interpreting a null.

Discriminating measurement: first run the independent retail oracle with the
whole-RDRAM control, title phase control, physical write watch
`0x00150000:0x00150008`, writer-PC histogram/post-value sampling, and the
existing predecessor execution range. Then build once and run the qualified
real-image/LLE/spin-yield/autopilot port arm with a phase-gated witness for
stores to `0x80150000..0x80150007`, including writer PC, address, value,
index, and the adjacent `0x8009131C` arguments. Matching writer/address/value
classes select `H-IndexSelection`; a first value difference selects
`H-TableWriterValue`; a first writer/address difference selects
`H-TableWriterRoute`; live controls with no table rows select
`H-TableObservationFailure`.

Exact route: run from `build/` with
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`,
`ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a'`,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and the existing phase,
caller, producer, and pre-call controls. Use direct-PID watchdog capture
under `scratch/agent/` and SIGKILL survivors. The oracle and port controls
must both be positive before any null is interpreted.
