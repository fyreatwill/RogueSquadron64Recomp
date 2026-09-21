# Next work unit: distinguish stale task publication from route sequencing

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3679 found one host execution thread for all observed audio-task
handoffs, source reads, and stage-2 rows: 1,254/1,254 stage rows had
`handoff_thread=1,event_thread=1`. Session 3678 still found dominant generation
mismatch and residual route drift. Do not repeat the thread-key instrument.

Competing hypotheses:

- H-StaleTaskPublication: source/stage callbacks use a carried generation that
  is older than the latest handoff on the same thread; the mismatch is a stale
  task record.
- H-RouteSequencing: carried generation is current at each callback, but route
  ordinal/row advances independently; the mismatch is route publication order.
- H-MixedPublication: both stale-generation and route-sequencing rows occur.

Discriminating measurement: add one atomic latest-M_AUDTASK generation and one
same-thread route-publication sequence to the existing source/stage rows, then
classify every stage-2 row by carried-generation==latest-generation and
carried-route==(latest route at callback). Same-thread stale generation with
stable route selects H-StaleTaskPublication; current generation with route drift
selects H-RouteSequencing; both select H-MixedPublication. Require the existing
positive controls in the same run: oracle whole-RDRAM, descriptor, title,
hangar, and type-2 controls plus port source/phase/ABI/stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3674_m5_stage_task_join.sh

Parse `[m5-source-range-reader]`, `[audtask-image-stage-row]`, and the new
latest-generation/route fields from
`scratch/agent/s3674_m5_stage_task_join/port.log`. Preserve the qualified route
and SIGKILL cleanup. Do not alter guest state or add a mitigation.
