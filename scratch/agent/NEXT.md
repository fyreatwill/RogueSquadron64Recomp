# Next work unit: re-qualify the M5 candidate-writer class after port gate failure

HYPOTHESIS-ID: m5-candidate-writer-census

Re-run the existing same-build retail-oracle/port census for the same candidate
PCs `0x8000512C`, `0x80005130`, and `0x80005134`; the retail arm selected H3,
but the paired port did not reach its required phase gate. Preserve the whole-RDRAM
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
- H4: the retail result remains H3, but the port route is still unevaluable;
  the phase-gated port arm stays pre-title or crashes before target entry.

Discriminator: the same-run oracle whole-RDRAM control must fire and both VI
phase controls must be present. Only then does candidate execution versus
post-store/scalar evidence select H1, H2, or H3. The paired port must reach
title and hangar without crash/abort and retain its qualified payload result;
otherwise the port arm is unevaluable rather than evidence about the retail
candidates.
