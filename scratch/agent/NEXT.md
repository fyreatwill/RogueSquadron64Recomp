# Next: task-generation/thread join at audio-task handoff

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3678 added a monotonic generation at the port `M_AUDTASK`
`get_rsp_microcode` handoff. The qualified run passed all controls and found 0
exact generation/route matches, 230 same-generation/different-route rows, and
1,671 different-generation/same-pointer rows. Generation mismatch dominates,
but route drift remains mixed evidence.

Competing hypotheses:

- H-SameThreadPublicationLag: handoff, source-reader, and stage creation run on
  one execution thread; different generations are stale route publication.
- H-CrossThreadOwnership: source and stage rows are created on different
  threads; generation mismatch reflects cross-thread task ownership.
- H-MixedThreadRoute: thread identity is stable for the 230 same-generation
  route drifts but splits the dominant different-generation rows.

Discriminating measurement: add one stable numeric execution-thread key at
audio handoff, source-reader, and image-stage-row creation, then classify all
stage-2 rows by generation equality, route equality, and thread equality in the
same run. Same-thread generation mismatches select H-SameThreadPublicationLag;
cross-thread mismatches select H-CrossThreadOwnership; a split selects
H-MixedThreadRoute. Require the generation/thread positive control in the same
run, plus oracle whole-RDRAM, descriptor, title, hangar, and type-2 controls and
port source-hook, source, phase, ABI, and stage controls.

Commands after implementing the bounded thread-key instrument:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3674_m5_stage_task_join.sh

Parse `m5-source-range-reader` and `audtask-image-stage-row` rows from
`scratch/agent/s3674_m5_stage_task_join/port.log`. Preserve the qualified route
and SIGKILL cleanup. Do not alter guest state or add a mitigation.
