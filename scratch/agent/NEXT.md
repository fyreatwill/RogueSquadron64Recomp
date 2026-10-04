# Next work unit: isolate first M5 audio-task entry across staging arms

HYPOTHESIS-ID: m5-audio-task-contract

Run one same-build three-arm capture that reaches or identifies the first
`M_AUDTASK`: declared-size + real audio, declared-size + silent audio, and
legacy-size + real audio. Preserve task-contract, DMEM-canary, DMA-range,
phase, crash-PC, and positive-control markers. Do not change the qualified
route or infer anything about the `0x800` boundary until the declared arm has
an audio-task row or a reproducible pre-audio failure separated from the
audio-arm choice.

Competing hypotheses:

- H1: declared-size + real and declared-size + silent both reach the first
  audio task, while legacy reaches it too; a declared-only post-`0x800` read
  or consumer identifies the contract failure.
- H2: declared-size fails before audio dispatch in both audio-arm settings,
  while legacy reaches audio; the defect is pre-audio setup/scheduling, not a
  proven need for over-copy.
- H3: the three arms do not provide matching positive controls or split the
  failure boundary, so the contract remains unevaluable and needs a different
  discriminator.

Discriminator: in one capture, require all three arms to emit the RSP-source
positive control and either an `audtask-first-boundary`/`audtask-abi` row or a
crash-PC row. H1 is a declared-only post-`0x800` consumer/read; H2 is the same
pre-audio failure for both declared arms with legacy audio entry; H3 is any
missing control or unresolved arm split.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3991_m5_task_contract_isolation.sh
