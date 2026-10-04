# Next work unit: retail-grounded source census at 0x800052A0

HYPOTHESIS-ID: m5-source-writer-census

Competing hypotheses:

- H1: one or more candidate PCs in the next retail-grounded class write the
  missing source payload during the target phase.
- H2: the candidate class is absent from qualified retail target/post-target
  evidence while the paired legacy port reaches both target phases.
- H3: the paired port route fails before target or the retail controls do not
  qualify, so this class is unevaluable and must not be called absent.

Discriminator: one same-build retail oracle and paired legacy/real capture for
the next three candidate PCs beginning at `0x800052A0`. The retail
whole-RDRAM/title/hangar controls and the port title/hangar controls must fire.
Candidate hits, post-target rows, and scalar/sequence evidence select H1 or H2;
any missing phase control selects H3.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4022_m5_candidate_writers.sh
```

Record the independent retail controls, candidate-PC evidence, and paired-port
phase qualification. Do not infer writer absence from a pre-target port route.
