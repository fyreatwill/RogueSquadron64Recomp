# Next work unit (s4421): qualify selector-table writer parity

HYPOTHESIS-ID: m5-selector-table-writer-boundary

The s4421 repair made both durable hooks live: the port capture emitted 4 table
stores and 4 store-context rows, with 1,007 caller and 2,014 pre-call rows and
all phase/task/image/filter controls live. The writer is now observable, but
this run did not include paired retail writer values or an explicit
store-to-load join.

Competing hypotheses:

- H-writer-value: retail and port store different legitimate table values before the selector load.
- H-index-value: paired stores agree, but the selector index differs at the later load.
- H-init-route: retail and port still execute different initializer/store routes despite live port hooks.
- H-join-failure: the retail writer arm or store-to-load join is not positively qualified.

Discriminating measurement: one paired retail/port capture must pass its
independent positive controls and retain writer/store-context rows plus the
later `0x80150000` load. Different legitimate stores select H-writer-value;
matching stores with different load indices select H-index-value; live controls
with a missing retail writer selects H-init-route; failed controls select
H-join-failure.

Exact commands:

1. Run the retail oracle writer arm with whole-RDRAM and VI/task positive
   controls, then the qualified port arm with the same phase-keyed logging.
2. Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run the port from `build/` with `ROGUESQ_LLE_FORCE=1`,
   `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`,
   `ROGUESQ_AUDIO_UCODE=1`, the canonical autopilot,
   `ROGUESQ_LOG_M5_SELECTOR_TABLE=1`,
   `ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1`,
   `ROGUESQ_LOG_M5_SELECTOR_INPUT=1`, `ROGUESQ_LOG_M5_SELECTOR_CALLER=1`,
   `ROGUESQ_LOG_M5_SELECTOR_PRECALL=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
   `ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`, and `ROGUESQ_LOG_ALL=1`.
4. Kill with SIGKILL. Require selector/table, caller/precall, VI, task, image,
   and positive-control markers in both arms before interpreting any null.
