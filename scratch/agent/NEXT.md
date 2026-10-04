# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-census

Run the paired retail/port candidate-writer harness with its three candidate
PCs set to `0x800050A8`, `0x800050AC`, and `0x800050B0`. Build the Debug
target first; retain whole-RDRAM, title-1024, hangar-512, oracle-completion,
and passive M5 controls.

Competing hypotheses:

- H1: at least one candidate writes the qualified retail hangar payload.
- H2: candidates execute in the target phase but produce no post-target row or
  scalar sample; this bounded class is not the payload writer.
- H3: candidates do not execute in the qualified target phase; this bounded
  class is not the payload writer.
- H4: a positive control or paired port arm fails, so the census is unevaluable.

Discriminator: all three candidate PCs must be measured in one retail run with
the positive controls passing. Target-phase execution, post-target rows, and
scalar samples split H1/H2/H3; any missing control or port hangar phase selects
H4 and invalidates the census.

Exact preparation and run:

    sed -i '' 's/0x8000509C,0x800050A0,0x800050A4/0x800050A8,0x800050AC,0x800050B0/' scratch/agent/run_s3941_m5_candidate_writers.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3941_m5_candidate_writers.sh
