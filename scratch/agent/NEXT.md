# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-census

Run one paired retail/port candidate-writer census for `0x800050E4`,
`0x800050E8`, and `0x800050EC`. Patch
`scratch/agent/run_s3941_m5_candidate_writers.sh` by changing its output
directory and all three `--post-value-pc`/grep addresses, then build and run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3941_m5_candidate_writers.sh

Keep the whole-RDRAM, title-1024, hangar-512, oracle-completion, scalar
mismatch, and passive M5 controls. The independent oracle positive control
must fire before trusting any null.

Competing hypotheses:

- H1: at least one candidate writes the qualified retail hangar payload.
- H2: candidates execute in the target phase but produce no post-target row
  or scalar sample.
- H3: candidates do not execute in the qualified target phase.
- H4: a positive control or paired port arm fails, making the census
  unevaluable.

Discriminator: with all controls passing in one run, target-phase execution,
post-target rows, and scalar samples split H1/H2/H3; any missing control or
port hangar phase selects H4. The preceding `0x800050D8/0xDC/0xE0` class
selected H3: all three were absent from the qualified retail phase, while
the port produced 2,997 image-DMA joins with zero-valued payload.
