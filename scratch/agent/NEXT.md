# Next work unit (s4420): repair durable selector-table writer witnesses

HYPOTHESIS-ID: m5-selector-table-writer-boundary

The s4419 run passed phase/task/image/filter controls and emitted 1,008 caller
and 2,016 pre-call rows, but emitted zero table-store and store-context rows.
The static artifact and script census shows `apply_s3509` and `apply_s3516`
are standalone and are not wired into the durable regeneration path. Repair
that coverage before attempting the writer boundary again.

Competing hypotheses:

- H-writer-value: after the hooks are wired, a port writer legitimately stores
  a different selector-table value before `0x8009131C`.
- H-index-value: after the hooks are wired, the table is equivalent but the
  selector index differs before the load.
- H-init-route: after the hooks are wired, the port takes a different
  initializer/route and never executes the retail writer.
- H-join-failure: the repaired hooks or phase/task controls remain absent, so
  the boundary is still unevaluable.

Discriminating measurement: first a static check must find both durable hook
calls in the generated artifact, then one phase-keyed run must include the
selector-table writer/store-context/input, caller/precall, VI, task, image, and
positive-control logs. Writer rows joined to the later `0x80150000` load split
H-writer-value from H-index-value; absent writer rows with live controls selects
H-init-route; failed controls selects H-join-failure.

Exact commands:

1. Wire `apply_s3509_m5_selector_table.py` and
   `apply_s3516_m5_selector_store_context.py` into the durable fixup helper;
   verify both markers in `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`.
2. Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run from `build/` with `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
   `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_AUDIO_UCODE=1`,
   the canonical autopilot, `ROGUESQ_LOG_M5_SELECTOR_TABLE=1`,
   `ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1`,
   `ROGUESQ_LOG_M5_SELECTOR_INPUT=1`, `ROGUESQ_LOG_M5_SELECTOR_CALLER=1`,
   `ROGUESQ_LOG_M5_SELECTOR_PRECALL=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
   `ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`, and `ROGUESQ_LOG_ALL=1`.
4. Kill with SIGKILL. Require the selector/table, caller/precall, VI, task,
   image, and positive-control markers before interpreting any null.
