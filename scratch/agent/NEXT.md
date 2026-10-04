# Next work unit: M5 candidate-writer census

HYPOTHESIS-ID: m5-candidate-writer-census

The route prerequisite is now qualified only for image/LLE-on. Resume the
already-batched retail/port census for `0x800051A4`, `0x800051A8`, and
`0x800051AC`; do not add a mitigation or infer global writer absence.

Competing hypotheses:

- H1: one candidate executes during a qualified retail title/hangar phase and
  produces a post-store scalar or destination payload.
- H2: a candidate executes in retail but produces no qualified payload, so the
  measured writer edge is elsewhere.
- H3: none of the candidates executes in the qualified phase; this bounded
  PC class is not the writer.

Discriminator: one build and one batched driver must pass the independent
whole-RDRAM positive control, reach retail VI 1024 and VI 512 plus oracle
completion, and report target-phase execution, post-store scalar records,
scalar mismatches, and candidate-to-payload joins for all three PCs. H1 is
selected by a qualified candidate payload; H2 by execution without payload;
H3 by zero candidate execution with positive controls intact.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3975_m5_candidate_writers.sh

The existing recipe is self-contained and uses SIGKILL cleanup, phase-gated
title/hangar controls, and the passive M5 markers. Keep the route result from
s3973 separate from this retail writer discriminator.
