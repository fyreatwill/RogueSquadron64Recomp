# Next work unit: explain declared-size M5 audio task-contract failure

HYPOTHESIS-ID: m5-audio-task-contract

Run the existing same-build two-arm task-staging capture to compare declared
`ucode_data_size=0x800` against legacy `0xF80` staging. Preserve task-contract,
DMEM-canary, DMA-range, phase, crash-PC, and payload controls. Identify the
first declared-arm consumer/read past the staged boundary before changing the
qualified route.

Competing hypotheses:

- H1: declared-size reaches the same task boundary as legacy and its first
  failing consumer is identified, proving the crash is downstream of staging.
- H2: declared-size fails before any consumer/read beyond `0x800` is observed,
  identifying a producer/setup defect rather than an over-copy requirement.
- H3: controls are incomplete or the failure signature is not reproducible, so
  the contract remains unevaluable.

Discriminator: in one capture, require both arms to emit task ABI rows and
DMEM-canary controls. H1 is a declared-arm crash after a traceable read/use of
bytes beyond `0x800`; H2 is a reproducible earlier crash with no such read/use;
H3 is any missing positive control or non-reproducible arm.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3977_m5_task_staging.sh
