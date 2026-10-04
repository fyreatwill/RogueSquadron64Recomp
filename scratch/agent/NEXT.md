# Next work unit: qualify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-census

Run the existing same-build retail-oracle/port census for candidate PCs
`0x80005144`, `0x80005148`, and `0x8000514C`. Preserve the whole-RDRAM
positive control, title VI 1024, hangar VI 512, oracle completion, and the
phase-gated image-DMA payload controls. Build first:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Then run `zsh scratch/agent/run_s3957_m5_candidate_writers.sh` from the
repository root. The runner launches retail and port concurrently, watchdogs
both, and kills them with SIGKILL. Do not advance the candidate range unless
the port reaches title VI 1024 and hangar VI 512 in the same run.

Competing hypotheses:

- H1: at least one candidate is a qualified retail writer; it executes in the
  target phase and produces a post-store row or scalar sample.
- H2: the candidates execute in qualified retail phases but are not writers
  of the target payload; they have no post-target row or scalar sample.
- H3: the candidates are outside the qualified retail path; they have no
  target-phase execution, post-target row, or scalar sample.
- H4: the retail result is H3, but the port route is unevaluable; the
  phase-gated port arm stays pre-title or crashes before target entry.

Discriminator: the same-run oracle whole-RDRAM control must fire and both VI
phase controls must be present. Only then does candidate execution versus
post-store/scalar evidence select H1, H2, or H3. The paired port must reach
title and hangar without crash/abort and retain its qualified payload result;
otherwise the port arm is unevaluable rather than evidence about the retail
candidates.
