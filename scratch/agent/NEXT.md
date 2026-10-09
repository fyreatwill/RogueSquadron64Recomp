# Next work unit (s4422): identify the retail title initializer/store route

HYPOTHESIS-ID: m5-selector-title-init-route

Session 4422 passed the paired positive controls. Retail reached the selector
load 2,253 times and wrote the table only in hangar, with values matching the
port's hangar stores. The port also wrote title values, so the next boundary is
the retail title initializer/store route.

Competing hypotheses:

- H-retail-title-writer: a retail title writer exists in an earlier or different
  address range than the observed table stores.
- H-retail-title-preinitialized: retail reaches the title load with a table
  value established before the phase-gated route.
- H-retail-title-bypass: retail's title selector path bypasses the table-store
  route entirely while still reaching the load PC.
- H-join-failure: the widened retail writer census or phase join is still not
  positively qualified.

Discriminating measurement: one retail oracle capture must pass whole-RDRAM,
VI, task/image, and selector-load controls, retain the matching hangar writer
as a positive control, and enumerate all title executions/writes in the known
selector caller/preceding range plus the physical table addresses. A title
writer row selects H-retail-title-writer; a live title load with no writer in
the widened range leaves preinitialization versus bypass to the table value/
index fields; failed controls select H-join-failure.

Exact commands:

1. Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
2. Run the retail oracle from the repo root with `--watch-write 0x0:0x800000`,
   physical table watches `0x00149758:0x0014975C` and
   `0x0014975C:0x00149760`, `--watch-pc-range 0x8008E000:0x80091340`,
   phase-gated title/hangar buckets, and the known selector-load PC.
3. Run the qualified port arm concurrently from `build/` with
   `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_AUDIO_UCODE=1`, the canonical autopilot,
   and the existing selector table/store-context/caller/pre-call/task/filter
   logging.
4. Kill with SIGKILL. Require selector/table, caller/precall, VI, task, image,
   and positive-control markers in both arms before interpreting any null.
