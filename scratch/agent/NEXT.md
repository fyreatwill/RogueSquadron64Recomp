# Next: exact-join sparse image-stage exceptions to source DMA

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3675 found title alternate task pointers at route ordinals 1, 460,
and 463, with varying stage-2 destinations, and a hangar alternate at ordinal
464. This favors route-sequence selection but does not yet exclude stale
callback timing because source-reader and stage rows lack one shared event key.

Competing hypotheses:

- H-ExceptionDestination: sparse pointer changes are selected by the image
  destination/window, not by the source-span input route.
- H-ExceptionRoute: sparse pointer changes follow a distinct route ordinal or
  route-row sequence; destination is only correlated.
- H-ExceptionTiming: sparse rows are stale/current-task timing at the stage
  callback and do not represent the task that supplied the source DMA.

Discriminating measurement: in one build/run, add a bounded shared event key
to both the stage witness and source-DMA witness, retaining route identity,
live task pointer, and destination/window. Join each sparse stage row to its
source-DMA event and preceding/following task rows. A stable destination map
selects H-ExceptionDestination; a route-sequence map selects H-ExceptionRoute;
an event-joined source pointer disagreeing with the callback pointer selects
H-ExceptionTiming. Require oracle whole-RDRAM, title, hangar, type-2,
RSP-source, source-span, and stage-row positive controls in the same run.

Exact recipe base:

    cmake --build build -j8
    zsh scratch/agent/run_s3674_m5_stage_task_join.sh

For the next build, modify only the existing stage/source diagnostics in
`src/main/main.cpp` and caller-side event propagation. Preserve the qualified
route (`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`,
`PROBE_LEAVE_OK=1`) and SIGKILL cleanup. Do not alter guest state or add a
mitigation.
