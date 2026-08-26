# NEXT work unit (s2367) — M5 payload provenance owner join

HYPOTHESIS-ID: m5-payload-transformation-provenance

## Work unit

Run one same-build refinement of the existing stub/image pair. Retain every
s2361–s2366 route, oracle, VI, task-ABI, image-stage, service/slot,
filter/voice, PCM, and crash/abort control. For each changed destination/length
candidate, assign every source/consumer event to its owning task interval,
record the candidate/task ordinal and completion ordering, and retain writer
fields. Do not change task data, field writeback, consumer/default behavior, or
add a guard.

## Competing hypotheses and discriminating measurement

- H-LegitimateTransformSource: a changed-payload candidate has a nonzero
  writer/source relation, source/consumer events assigned to one stable task
  ordinal, and ordered completion; this identifies a source class but does not
  authorize writeback.
- H-MixedOrUnrelatedCandidate: changed-payload candidates exist but have no
  coherent source/consumer/completion relation in the retained phase.
- H-NoChangedCandidate: the expanded table has no changed-payload candidate.
- H-TimingCaptureInvalid: a required oracle, route, or positive control is
  absent; no contract conclusion is valid.

The discriminator is one complete table with every target-stage row, every
same-destination/length payload variant, all phase-scoped source/consumer
tuples, each event's owning task ordinal, completion event, writer/source fields,
and ordering deltas. Select `H-LegitimateTransformSource` only if both arms
retain the positive controls and a changed candidate has a nonzero writer/source
relation plus same-task ordered completion. A changed candidate with only
zero-payload source/consumer rows selects `H-MixedOrUnrelatedCandidate`.

## Exact commands

    apply_patch < persistent payload-owner-join parser and driver patch
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2366_m5_payload_transformation_provenance.sh s2366_m5_payload_transformation_provenance
    grep -E '^(controls|table|verdict) ' scratch/agent/s2366_m5_payload_transformation_provenance/driver.log

The driver must run the retail oracle before the port arms, launch both arms
from the same build, use VI-gated controls, and kill game processes with
SIGKILL. Reject any null result without same-run positive controls. A source
relation is evidence about provenance only; no behavior change is authorized.
