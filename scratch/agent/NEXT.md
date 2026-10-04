# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-class

Run the existing phase-gated retail/port discriminator for the next adjacent
unclassified candidate set, exactly `0x80004FA0`, `0x80004FA4`, and
`0x80004FA8`:

    zsh scratch/agent/run_s3916_m5_remaining_candidate_writers.sh

Competing hypotheses:

- H1: one or more PCs execute in the qualified retail target phase and produce
  a post-target scalar value, identifying a candidate writer at this scope.
- H2: PCs execute or have candidate-span rows, but produce no qualified
  post-target scalar value; the class remains unresolved/indirect at this
  scope.
- H3: none executes in the qualified retail target phase, selecting absence for
  this bounded class only.

Discriminator: the same-run retail whole-RDRAM, title-1024, and hangar-512
positive controls must pass; then compare target-phase execution, post-target
rows, and scalar samples for all three PCs. The paired port arm must be
reported separately and does not establish retail writer absence.

Keep the M3 heap-guard validation parked until a configured `PatchesLib` target
and MIPS toolchain are available. Do not add another guard.
