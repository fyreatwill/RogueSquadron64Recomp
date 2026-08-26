# NEXT work unit (s2363) — M5 stage/output contract join

HYPOTHESIS-ID: m5-stage-output-contract-join

## Work unit

Run one same-build refinement of the existing stub/image pair. Retain every
s2361 route, oracle, VI, task-ABI, image-stage, service/slot, filter/voice,
PCM, and crash/abort control. Use the s2362 containing task ordinal to join
each target stage to its stage payload, generated DMA destination,
source/consumer PCM rows, and completion ordering. Do not change task data,
field writeback, consumer/default behavior, or add a guard.

## Competing hypotheses and discriminating measurement

- H-ContainingTaskOutputClosed: the containing task has a legitimate
  stage/output or PCM relation with matching ordering.
- H-ContainingTaskInternalOnly: the stage is inside the task, but its payload,
  DMA destination, and source/consumer PCM rows do not close to that task.
- H-TimingCaptureInvalid: a required oracle, route, stage, or positive control
  is absent; no contract conclusion is valid.

The discriminator is one complete table with every target-stage row, its
containing task ordinal, stage payload/destination, task DMA ranges, PCM
source/consumer events, and completion ordering. Select one hypothesis only
if both arms retain the positive controls and the table is nonempty.

## Exact commands

    apply_patch < persistent stage/output parser and driver patch
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2363_m5_stage_output_contract_join.sh s2363_m5_stage_output_contract_join
    grep -E '^(controls|table|verdict) ' scratch/agent/s2363_m5_stage_output_contract_join/driver.log

The driver must run the retail oracle before the port arms, launch both arms
from the same build, use VI-gated controls, and kill game processes with
SIGKILL. Reject any null result without same-run positive controls.
