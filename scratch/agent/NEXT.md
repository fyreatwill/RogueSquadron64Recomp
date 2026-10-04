# Next work unit: qualify the 0x800052AC candidate class

HYPOTHESIS-ID: m5-candidate-writer-class-052c

Competing hypotheses:

- H1: one or more candidate PCs `0x800052AC`, `0x800052B0`, or
  `0x800052B4` writes the retail target span during the qualified target
  phase.
- H2: all three candidates remain absent in qualified retail target/post-
  target evidence while the port reaches both target phases, selecting the
  next writer class.
- H3: retail controls or either real-audio port arm fails before the target
  comparison, so the class is unevaluable and the route discriminator must
  be repaired before interpreting candidate absence.

Discriminator: one same-build capture using the fixed candidate recipe, with
retail whole-RDRAM/title/hangar/completion controls, candidate PC watches, and
declared/real plus legacy/real port phase/audio/image controls. H1 requires a
candidate hit or post-target writer row in retail. H2 requires no candidate
or post-target writer evidence, all retail controls, and both real-audio port
arms at target phase. H3 is any missing positive control or pre-target arm
failure. Do not change audio behavior or add a second build/run arm.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4024_m5_candidate_writers.sh
```

Require the positive-control threshold, retail title and hangar VI markers,
oracle completion, and both port target phases before accepting a null.
