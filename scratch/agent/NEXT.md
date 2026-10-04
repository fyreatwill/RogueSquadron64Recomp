# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class

Run one qualified legacy/real paired census for the next adjacent candidate
set after `0x8000523C`: `0x80005240`, `0x80005244`, and `0x80005248`.
The independent retail oracle and the paired port must both reach their
positive phase controls before a null is interpreted.

Competing hypotheses:

- H1: at least one candidate writes nonzero target/post-target payload at a
  matching task ordinal; this identifies a qualified producer edge.
- H2: all three candidates remain absent or zero in retail target/post-target
  evidence while the paired legacy port reaches phase 5; this class is not the
  missing nonzero writer at the measured scope.
- H3: an arm fails its whole-RDRAM, title, hangar, or port phase control, so
  the candidate result is unevaluable and the census must not advance.

Discriminator: in one run, compare the oracle's positive-control and phase
counts with each candidate's `seen`, post-target, scalar-store, and task-join
rows, alongside the port's phase-5/task controls. H1 requires a candidate
post-target nonzero/scalar row joined to a matching task ordinal; H2 requires
all three candidates to have no such row with both arms qualified; H3 is any
missing control or crash/abort before qualification.

Exact command:

    zsh scratch/agent/run_s3998_m5_candidate_writers.sh

The script launches the retail oracle and legacy/real port arm concurrently,
captures logs under `scratch/agent/s3998_m5_candidate_writers/`, and SIGKILLs
both after its bounded window. Do not add another field or run a second soak
in this iteration.
