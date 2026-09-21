# Next: classify sparse image-stage task-pointer exceptions

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3674 found phase-dominant stage-task matches but sparse exceptions:
title stage 2/3 had two `0x80173B20` rows each, and hangar stage 2/3 had one
`0x80171CE0` row each. The source-reader route ordinal did not align with the
stage ordinal in that run, so exact ownership is still open.

Competing hypotheses:

- H-ExceptionDestination: sparse pointer changes are selected by the image
  destination/window, not by the source-span input route.
- H-ExceptionRoute: sparse pointer changes follow a distinct route ordinal or
  route-row sequence; destination is only correlated.
- H-ExceptionTiming: sparse rows are stale/current-task timing at the stage
  callback and do not represent the task that supplied the source DMA.

Discriminating measurement: in one build/run, add a bounded stage witness of
the complete route identity plus live task pointer and destination/window, and
join it to the source-DMA event using the shared audio event/route sequence.
Report all sparse rows and their preceding/following task rows. A stable
destination mapping selects H-ExceptionDestination; a route-sequence mapping
selects H-ExceptionRoute; disagreement between callback pointer and the
event-joined source pointer selects H-ExceptionTiming. Require oracle
whole-RDRAM, title, hangar, type-2, RSP-source, source-span, and stage-row
positive controls. Keep both phase arms in the same run; no guest-state rewrite
or mitigation.

Exact recipe base:

    cmake --build build -j8
    zsh scratch/agent/run_s3674_m5_stage_task_join.sh

The next script must preserve the qualified route:
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, `PROBE_LEAVE_OK=1`, and the
existing autopilot/phase gate. Use SIGKILL cleanup and capture from `build/`.
