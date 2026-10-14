# Next work unit

HYPOTHESIS-ID: m5-a10-guard-class

WORK UNIT: execute one bounded M5 Step 8 A10 pointer/list/table guard-class
qualification. First establish the independent retail whole-RDRAM control and
the named writer/range/voice-traversal controls; then compare the current guard
class with one same-build rollback arm. Do not relax a guard unless the writer
and legitimate in-range value are both observed. If the controls do not reach
the target phase, stop and report the route as unevaluable.

Competing hypotheses:

* H-A10-legitimate: the guarded pointer/list/table values are legitimate on
  the qualified route, so the guards are dormant and not the audio defect.
* H-A10-suppression: a guard fires after a legitimate writer publishes an
  in-range value, and the guard suppresses required voice/reap work; the
  rollback arm changes downstream traversal while retaining route controls.
* H-A10-invalid: the writer publishes an out-of-range value or the route never
  reaches the guard phase, so any null is invalid for a guard-removal decision.

DISCRIMINATING MEASUREMENT: one phase-gated table must join, in the same run,
the retail whole-RDRAM positive control, retail writer/range evidence, port
writer and pointer values, guard-fire counts by site, valid traversal/slot
transitions, PCM source/consumer rows, and title/hangar route controls. A guard
fire after a named legitimate in-range write with downstream rollback
divergence selects H-A10-suppression; no guard fire with valid traversal selects
H-A10-legitimate; missing controls or invalid values selects H-A10-invalid.

Ground-truth gate before building: use the documented retail-oracle route and
positive controls from docs/M5-AUDIO-PLAN.md; do not add a narrow instrument
until the whole-RDRAM watch and route phase controls are armed.

Exact preparation:

    rg -n 'A10|voice-list|table|guard' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md
    sed -n '118,153p' docs/M5-AUDIO-PLAN.md
    sed -n '208,225p' docs/M5-AUDIO-PLAN.md

Build every rollback arm in one build, run from build/ with the ROM present,
phase-gate on VI transitions, and enqueue the soak rather than babysitting it.
