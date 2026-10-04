# Next work unit: qualify the declared-real first-audio control, then census consumers

HYPOTHESIS-ID: m5-audio-task-contract

The s3993 rerun did not qualify the planned discriminator: declared/real
crashed in `spTaskSchedulerThread` before an audio ABI row, while the silent
and legacy controls progressed. Re-run the same-build three-arm capture after
making the declared/real arm emit a bounded first-audio control, and retain
the post-`0x800` read/consumer table only as interpretation data. Do not claim
consumer absence from an arm with no real-audio ABI row.

Competing hypotheses:

- H1: declared/real can reach the first audio ABI and exposes a declared-only
  read or consumer beyond `0x800` at a matching task ordinal.
- H2: declared/real reaches the ABI and its consumer reads match legacy/real;
  the `0xF80` copy is not required by the observed path.
- H3: declared/real remains unable to reach the ABI, so the task-contract
  boundary—not the consumer table—is the active blocker.

Discriminator: one capture must have all three arms emit the RSP-source canary,
the first real-audio ABI control, and target-phase controls. H1/H2 require a
declared/real ABI row; H1 is a declared-only post-`0x800` read, H2 is matching
declared/legacy reads, and H3 is a missing declared/real ABI control. The
silent arm is only a control for the stubbed no-DMEM-change path.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3991_m5_task_contract_isolation.sh

Expected evidence: summarize per-arm canary, ABI, phase, crash, and consumer
counts with `rg`/`tail`; do not read a full log.
