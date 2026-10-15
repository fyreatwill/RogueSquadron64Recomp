# Next work unit

HYPOTHESIS-ID: m5-a12-yield-validation

Run the existing A12 wait-boundary validation in one rebuilt binary, comparing
default yielding against the explicit rollback arm. This is the next M5 audio
step after the synth-registration mitigation was retired.

Competing hypotheses:

- H1: default A12 yielding is the correct producer/scheduler contract; it
  records producer arm/clear and wait-return rows and preserves task/SP,
  slot, PCM, title, and hangar controls, while rollback differs or stalls.
- H2: the default yield changes no qualified behavior; both arms have the same
  positive controls and route outcome, so A12 is already behavior-neutral.
- H3: yielding is harmful on the current route; default loses a positive
  control, crashes, or diverges while rollback remains qualified.

Discriminator: one build and `tools/run_m5_yield_ab.sh`, with both arms
phase-gated. Require producer arm/clear and wait-return controls, task/SP,
slot transition, nonzero PCM source/consumer joins, title/hangar, and
crash/abort markers in both arms. H1 selects the default de-stub; H2 closes
A12 without further behavior change; H3 keeps the rollback/default decision
open and identifies the failed contract boundary.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh tools/run_m5_yield_ab.sh

Do not start the generated-symbol sweep while this M5 unit is applicable.
