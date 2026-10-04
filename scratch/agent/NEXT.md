# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class

Run the phase-gated retail/port discriminator for candidate PCs
`0x80004FF4`, `0x80004FF8`, and `0x80004FFC`, using the established corrected
wrapper pattern from `run_s3924_m5_remaining_candidate_writers.sh`.

Competing hypotheses:

- H1: one or more candidates is the qualified retail writer; its target-phase
  execution and post-target scalar attribution should coincide with a retail
  target-buffer value.
- H2: candidates execute and touch the candidate span, but none is the
  qualified writer; candidate-span rows occur without post-target attribution.
- H3: candidates do not execute in the qualified target phase; the class is
  disconnected from the measured retail writer path.

Discriminator: in one run, require retail whole-RDRAM, title-1024, hangar-512,
and oracle-completion positive controls, then classify each PC by target-phase
execution, candidate-span rows, post-target rows, and scalar samples. The port
arm must also report hangar reachability, crash/abort status, image-DMA joins,
and qualified payload FNV/nonzero count. Do not infer global writer absence.

Exact command: `zsh scratch/agent/run_s3925_m5_remaining_candidate_writers.sh`.
