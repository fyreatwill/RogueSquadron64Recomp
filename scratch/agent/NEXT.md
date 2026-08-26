# NEXT work unit (s2362) — M5 task-to-stage timing join

HYPOTHESIS-ID: m5-task-stage-timing-join

## Work unit

Make one bounded parser/driver refinement of the existing s2361 same-build
stub/image pair. Retain every s2361 route, oracle, VI, task-ABI, image-stage,
service/slot, filter/voice, PCM, and crash/abort control. Expand the event
table around each target image stage so it searches the complete nearby ordinal
stream, not only the current same-task pre/post window. Do not change task
data, field writeback, consumer/default behavior, or add a guard.

## Competing hypotheses and discriminating measurement

- H-StageJoinsEarlierTask: target-stage rows join an earlier task ordinal;
  current same-task zeroes are an ordering/window artifact.
- H-StageJoinsLaterTask: target-stage rows join a later task ordinal;
  the stage is emitted after the current task lifecycle closes.
- H-StageHasNoTaskJoin: target-stage rows join no task ordinal in the complete
  bounded stream while all positive controls remain intact.
- H-TimingCaptureInvalid: the expanded table loses a required positive control,
  route phase, or target-stage coverage; no timing conclusion is valid.

The discriminator is a single table with every target-stage row, nearest task
ordinals before/after it, event deltas, phase key, and arm. Select exactly one
hypothesis only if oracle, route, VI, ABI, image-stage, and PCM controls remain
positive and the target rows are present in both required arms/phase scope.

## Exact commands

    apply_patch < timing-join parser/driver patch recorded before the build
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2362_m5_task_stage_timing_join.sh s2362_m5_task_stage_timing
    grep -E '^(controls|table|verdict) ' scratch/agent/s2362_m5_task_stage_timing/driver.log

The parser change must be in the persistent script before the build/run and
must write the complete ordinal table under the output directory. Reject any
null result without the same-run positive controls, and kill game processes
with SIGKILL through the driver watchdog.
