# Next work unit (s4419): qualify the selector-table writer boundary

HYPOTHESIS-ID: m5-selector-table-writer-boundary

The s4418/s4417 coverage defect is closed. The repaired fixup and regen helper
retain the caller/precall witnesses. The qualified port run showed title-phase
pre-call values `0x801919B0`, `0x801772F0`, and `0x80175960`, while retail's
title boundary showed `0x801772F0` in every sampled row.

Competing hypotheses:

- H-writer-value: a port writer legitimately stores a different selector-table
  value before `0x8009131C`.
- H-index-value: the table is equivalent but the selector index differs before
  the load.
- H-init-route: the port takes a different initializer/route and never executes
  the retail writer.
- H-join-failure: writer rows or phase/task controls are absent, so the boundary
  is unevaluable.

Discriminating measurement: one phase-keyed run must include the existing
selector-table writer/store-context/input, caller/precall, VI, task, image, and
positive-control logs. Writer rows joined to the later `0x80150000` load split
H-writer-value from H-index-value; absent writer rows with live controls selects
H-init-route; failed controls selects H-join-failure.

Exact commands:

1. Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
2. Run from `build/` with `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
   `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_AUDIO_UCODE=1`,
   the canonical autopilot, `ROGUESQ_LOG_M5_SELECTOR_TABLE=1`,
   `ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1`,
   `ROGUESQ_LOG_M5_SELECTOR_INPUT=1`, `ROGUESQ_LOG_M5_SELECTOR_CALLER=1`,
   `ROGUESQ_LOG_M5_SELECTOR_PRECALL=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
   `ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`, and `ROGUESQ_LOG_ALL=1`.
3. Kill with SIGKILL. Require the selector/table, caller/precall, VI, task,
   image, and positive-control markers before interpreting any null.
