# Next work unit: classify the next adjacent M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-census

Run one bounded census for candidate PCs `0x80005234`, `0x80005238`, and
`0x8000523C`, continuing the existing writer-class sweep with the qualified
legacy/real audio-DMA route. Keep the whole-RDRAM positive control and the
phase-gated target/post-target/scalar tables in the same build and run.

Competing hypotheses:

- H1: at least one candidate is a qualified retail writer and produces a
  nonzero target/post-target payload at a matching task ordinal.
- H2: candidates execute or are observed, but none produces qualified
  nonzero target/post-target payload in the retail target phases.
- H3: the candidate table or route controls fail, so the result is
  unevaluable rather than writer absence.

Discriminator: the same run must show the whole-RDRAM positive control and
both title VI 1024 and hangar VI 512 controls. H1 is a candidate-linked
nonzero payload with matching ordinal; H2 is zero candidate-linked target,
post-target, and scalar payload while the paired legacy port reaches both
phases; H3 is any missing positive control or incomplete qualified route.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    perl -pe 's/s3989_m5_candidate_writers/s3996_m5_candidate_writers/g; s/0x8000521C,0x80005220,0x80005224/0x80005234,0x80005238,0x8000523C/g; s/0x8000521C\\|0x80005220\\|0x80005224/0x80005234|0x80005238|0x8000523C/g' scratch/agent/run_s3989_m5_candidate_writers.sh > /tmp/rs64-s3996-candidates.sh
    env zsh /tmp/rs64-s3996-candidates.sh

Inspect only counts and tails from the generated logs; do not read a full
run log. If the source script name differs, make the equivalent bounded
substitution before building and preserve the same positive controls.
