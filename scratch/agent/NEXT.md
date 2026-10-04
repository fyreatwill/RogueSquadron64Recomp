# Next work unit: census first-audio consumers beyond the declared staging span

HYPOTHESIS-ID: m5-audio-task-contract

Add one phase-scoped read/consumer table at the first real `M_AUDTASK`, then
run the existing three-arm capture unchanged: declared-size + real audio,
declared-size + silent audio, and legacy-size + real audio. Preserve the
task-contract, DMEM-canary, DMA-range, phase, and positive-control markers.
Do not change the qualified route.

Competing hypotheses:

- H1: a declared-only read/consumer beyond the `0x800` staging span appears at
  a matching first-audio task ordinal.
- H2: declared and legacy have identical consumer reads; the `0xF80` copy is
  not required by the observed audio path.
- H3: the table is empty or only the silent control differs; the contract
  remains unevaluable and needs a different boundary.

Discriminator: in one capture, require all three arms to emit the RSP-source
positive control and the first real-audio ABI row. H1 is a declared-only
post-`0x800` read/consumer; H2 is matching declared/legacy reads; H3 is no
qualified read or a missing control. The silent arm is a control for the
stubbed no-DMEM-change path, not evidence about the real consumer.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3991_m5_task_contract_isolation.sh
