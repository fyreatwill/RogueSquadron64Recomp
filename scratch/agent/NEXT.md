# Next work unit: qualify M5 candidate writers 0x80005210–0x80005218

HYPOTHESIS-ID: m5-candidate-writer-census

Run the existing same-build retail/port candidate-writer census for
`0x80005210`, `0x80005214`, and `0x80005218`. Use the validated legacy audio
DMA rollback (`ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1`) on the port arm so the
declared-size task-contract crash cannot contaminate this writer qualification.
The existing instrument's whole-RDRAM, title-1024, hangar-512, oracle-done,
and paired port payload/task controls must all be reported.

Competing hypotheses:

- H1: at least one candidate executes in a qualified retail target phase and
  has a post-store/scalar sample, identifying a live writer candidate.
- H2: retail reaches all controls but all three candidates remain absent from
  target-phase, post-target, and scalar evidence; this bounded class is not a
  writer.
- H3: the port arm cannot qualify because the legacy rollback still fails or
  its source/task controls do not close, so this class is unevaluable.

Discriminator: compare the single-run retail candidate rows/post-store
samples with the independent whole-RDRAM and phase controls, then require the
paired port to reach title/hangar without crash/abort and with its existing
source/task joins. A candidate hit selects H1; clean retail absence with
qualified port selects H2; missing controls or a legacy-arm crash selects H3.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3988_m5_candidate_writers.sh
