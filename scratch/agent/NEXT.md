# Next work unit: extend the qualified M5 candidate-writer census

HYPOTHESIS-ID: m5-candidate-writer-census

Competing hypotheses:

- H1: at least one of `0x8000527C`, `0x80005280`, or `0x80005284` writes
  nonzero target/post-target payload at a matching task ordinal.
- H2: the route and controls qualify, but all three adjacent candidates remain
  absent from post-target samples/rows/sequence hits.
- H3: the port fails before both target phases, making this candidate class
  unevaluable and requiring route re-qualification before another sweep.

Discriminator: one same-run retail positive control plus title VI 1024 and
hangar VI 512 on the paired port, followed by a nonzero candidate row at a
matching task ordinal. A qualified nonzero row selects H1 and identifies a
producer edge; qualified zero rows select H2; a pre-target crash or missing
phase control selects H3.

Exact command:

    zsh scratch/agent/run_s4004_m5_candidate_writers.sh

The wrapper launches the retail oracle and legacy/real port arm concurrently,
captures both logs, and SIGKILLs both after the bounded window. Do not add
another field or run a second soak.
