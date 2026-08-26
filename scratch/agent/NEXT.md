# NEXT work unit (s2365) — M5 mixed-stage publication split

HYPOTHESIS-ID: m5-stage-output-contract-join

## Work unit

Run one same-build refinement of the existing stub/image pair. Retain every
s2361–s2364 route, oracle, VI, task-ABI, image-stage, service/slot,
filter/voice, PCM, and crash/abort control. For every target row, retain the
exact DMA tuple and destination/length candidates with any payload FNV or
nonzero value; join each candidate to post-task source/consumer PCM rows and
the containing task's later completion/publication update. Do not change task
data, field writeback, consumer/default behavior, or add a guard.

## Competing hypotheses and discriminating measurement

- H-MixedStageRole: one target row closes with exact post-task source,
  consumer, and completion evidence while another does not, even after
  destination/length candidate expansion.
- H-PayloadTransform: the unmatched target row has a post-task destination and
  length candidate, but its FNV/nonzero payload differs from the stage tuple.
- H-NoPostTaskPublication: the unmatched target row has no post-task candidate.
- H-TimingCaptureInvalid: a required oracle, route, or positive control is
  absent; no contract conclusion is valid.

The discriminator is one complete table with every target-stage row, its
containing task ordinal, exact DMA tuple, all same-destination/length payload
candidates, post-task source/consumer tuples, completion/publication event, and
ordering deltas. Select one hypothesis only if both arms retain the positive
controls and the table is nonempty.

Implementation note before build: extend the persistent parser and driver in
one batch to retain the s2364 exact-DMA result and all destination/length
candidates, then join those candidates to post-task PCM source/consumer events
and the latest containing-task completion record. One exact closed row plus one
unmatched row selects H-MixedStageRole; a changed payload on the unmatched row
selects H-PayloadTransform; no candidate selects H-NoPostTaskPublication; any
missing control selects H-TimingCaptureInvalid.

## Exact commands

    apply_patch < persistent mixed-stage candidate parser and driver patch
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2365_m5_mixed_stage_publication_split.sh s2365_m5_mixed_stage_publication_split
    grep -E '^(controls|table|verdict) ' scratch/agent/s2365_m5_mixed_stage_publication_split/driver.log

The driver must run the retail oracle before the port arms, launch both arms
from the same build, use VI-gated controls, and kill game processes with
SIGKILL. Reject any null result without same-run positive controls.
