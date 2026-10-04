# Next work unit: rerun the parked M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class-0594-qualified

Competing hypotheses:

- H1: retail executes one or more of `0x80005294`, `0x80005298`, or
  `0x8000529C` in the qualified title/hangar target phases; the prior null was
  hidden by the legacy route failure.
- H2: none of the three PCs is a qualified retail target/post-target writer;
  the legacy route failure is independent and must not be treated as writer
  absence.
- H3: the candidate evidence remains unevaluable because the legacy/real arm
  again fails before target phases, despite the declared/real control.

Discriminator: one build and one concurrent retail-oracle plus legacy/real and
declared/real capture using the existing phase-scoped writer table. Retail's
whole-RDRAM positive control, title VI 1024, and hangar VI 512 controls must
fire. If retail controls and candidate/post-target rows qualify, any candidate
hit selects H1; zero candidate/post-target evidence with a completed oracle
selects H2; a legacy pre-target failure while declared reaches both phases
selects H3 for route qualification and leaves the candidates unevaluable. Do
not infer OSTask fields from scheduler `a0`; use the existing ABI rows.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s4006_m5_candidate_writers.sh

The wrapper substitutes the candidate addresses in the existing s4005 recipe
and writes bounded summaries under `scratch/agent/s4006_m5_candidate_writers/`.
