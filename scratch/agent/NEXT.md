# Next work unit: new retail-grounded source-writer census

HYPOTHESIS-ID: m5-source-writer-class-052a

Competing hypotheses:

- H1: at least one of `0x800052A0`, `0x800052A4`, or `0x800052A8` writes a
  nonzero value in a qualified retail target phase and is the missing source
  writer.
- H2: all three candidates remain absent or zero in qualified retail target
  phases, while the lifetime histogram identifies a different writer family.
- H3: the route is not qualified again, so this candidate class is
  unevaluable and no writer conclusion is allowed.

Discriminator: one same-build concurrent retail/declared-real/legacy-real
capture using the existing oracle positive controls, title/hangar VI controls,
phase-scoped post-value PC watches, and port audio/RSP/phase controls. H1
requires a target-phase retail candidate hit with a nonzero value; H2 requires
qualified retail controls plus candidate-null evidence and a usable alternate
writer histogram; H3 is any missing retail positive control or either port arm
missing a target phase. A port-only null is not evidence about the writer.

Commands: copy `scratch/agent/run_s4005_m5_candidate_writers.sh` to
`scratch/agent/run_s4022_m5_candidate_writers.sh`, replace its candidate PCs
with `0x800052A0,0x800052A4,0x800052A8` and output tag with `s4022`, then run
`zsh scratch/agent/run_s4022_m5_candidate_writers.sh` from the repository root.
Build once with `cmake --build build --config Debug --target
RogueSquadron64Recomp`; run all arms concurrently and kill them with SIGKILL
through the recipe. Do not change audio behavior or add a mitigation.
