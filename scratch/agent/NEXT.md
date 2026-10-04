# Next work unit: classify the next M5 candidate-writer classes

HYPOTHESIS-ID: m5-candidate-writer-census

Test retail PCs `0x80004F94`, `0x80004F98`, and `0x80004F9C` with the existing
phase-gated oracle and paired port route. Keep any port pre-target failure or
zero image-DMA count separate from the retail writer result.

Competing hypotheses:

- H1: at least one candidate is a qualified retail writer for the target span;
  it produces a post-target scalar sample.
- H2: candidates execute in the qualified phase but produce no post-target
  scalar sample; this closes only this bounded class.
- H3: candidates do not execute in the qualified phase; this closes only this
  bounded class as unreachable.

Discriminator: retail whole-RDRAM, title-1024, and hangar-512 controls must
pass, then compare each candidate's qualified-phase execution, post-target
rows, and post-target scalar samples. Record the paired port outcome, but do
not infer image-DMA behavior from a run that lacks target-phase joins.

Exact command:

    zsh scratch/agent/run_s3914_m5_remaining_candidate_writers.sh

ORIGIN: no mitigation or guard is planned. Candidate PCs are independent
retail writer hypotheses; their legitimacy remains unresolved until the oracle
attributes a qualified post-target value.
