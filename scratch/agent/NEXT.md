# NEXT work unit — qualify target-phase audio/task route reachability

HYPOTHESIS-ID: m5-audio-route-target-reachability

## Single work unit

Run one paired image-arm/silent-arm qualification using the existing
phase-keyed audio/task/DMA/return/service/slot/voice/MORT/PCM table and the
VI consumer controls. The completed consumer probe stopped at VI 640, so
target-phase parity cannot be assessed until route reachability is established.
Do not change behavior.

## Competing hypotheses

- H-ImageReachesTarget: the corrected real Factor 5 image arm reaches 1024 or
  512 and supplies target-phase positive-control rows.
- H-SilentReachesTarget: only the silent arm reaches target phase, implicating
  image-task handling without authorizing a change.
- H-BothPreTarget: both arms stop before target phase, so audio/task rows are
  unevaluable and the route blocker is upstream of this table.

## Discriminating measurement

In one run, the positive-control prefix plus paired image/silent phase rows
split the hypotheses. Target-phase rows in the image arm select
H-ImageReachesTarget; target rows only in silent select
H-SilentReachesTarget; no target rows in either arm with live controls select
H-BothPreTarget.

## Exact commands

1. Use the existing phase-keyed audio/task/DMA/return/service/slot/voice/MORT/PCM
   diagnostic and build both image and silent arms in one build.
2. Run both arms from `build/` with the corrected image default and existing
   spin-yield/F5-LLE controls, capturing a whole-run positive control and VI
   phase lines to a new `scratch/agent/s3124_*` directory; kill with SIGKILL.
3. Record target-phase reachability and select exactly one hypothesis.
