# Next work unit: M5 pre-title route A/B

HYPOTHESIS-ID: m5-step1-pretitle-route

The Step 1 audio-chain comparison is unevaluable until the port reaches a
qualified phase. The concurrent pair stopped at VI 640 in both arms; the
sequential retry crashed in the silent arm at VI 320 during the Factor 5 boot
task. Do not change audio behavior or add a mitigation in the next unit.

Competing hypotheses:

- H1: LLE scheduling is the pre-title discriminator; the LLE-off image arm
  reaches VI 1024/512 while LLE-on and/or silent reproduces the failure.
- H2: the failure is audio-arm independent; all image/silent arms show the
  same VI-640 stall or boot-task crash regardless of LLE mode.
- H3: the result is an environment/build or stale-process failure; the
  positive port route control or executable/ROM check fails before comparable
  phase evidence.

Discriminator: one build and one driver must launch all arms (silent and image
with LLE on, image with LLE off), phase-gated on VI transitions, and record
for each arm VI 320/640/1024/512, Factor 5 boot/task dispatch and exit,
`last-guest-pc`, crash/abort markers, and process/ROM validation. H1 is
selected only if LLE-off changes the qualified phase outcome; H2 if all arms
share the same pre-title outcome; H3 if controls are not comparable.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s3973_m5_route_ab/run_fixed.sh

The driver must use SIGKILL cleanup, run from `build/`, and carry the passive
M5 markers and phase controls. Do not interpret any task/PCM null before a
title or hangar phase.
