# Next work unit: identify the branch that schedules the zero clear

HYPOTHESIS-ID: m5-source-clear-branch

S3707 selected `H-ProducerInputZero`: the shared `0x801797B0` object was
nonzero immediately before the legitimate zero clear in both paired arms.

Competing hypotheses:

- `H-ClearBranchRoute`: a route/phase branch intentionally schedules the clear
  before payload production.
- `H-ClearCallerState`: caller state is wrong and selects the zero-clear path.
- `H-ClearCallOrdering`: the same caller is reached in the wrong order relative
  to the producer setup.

Discriminator: one phase-gated caller table at `0x8008F2CC` and its immediate
predecessor branch, carrying route ordinal, caller PC/RA, branch outcome,
`a0/a1/a2`, and the last producer-family sequence. A stable route branch with
the same zero-clear arguments selects `H-ClearBranchRoute`; changed caller
state selects `H-ClearCallerState`; a producer sequence after the clear selects
`H-ClearCallOrdering`. Keep the existing positive controls and run real and
silent arms in one build/run.

Build:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run:

`zsh scratch/agent/run_s3707_m5_source_clear_input.sh`

Do not alter the clear or add a mitigation.
