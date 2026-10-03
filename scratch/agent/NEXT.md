# Next work unit: join one target-phase task contract to its input DMA

HYPOTHESIS-ID: m5-task-contract-input-dma-join

s3838 qualified the same-build target phases: logger-off and logger-on both
reached title VI `0x00790400`/1024 and hangar VI `0x006AB400`/512 with no
crash/abort. Logger-on emitted 1,962 `[audtask-abi]` rows and 1,024
task-lifetime rows; logger-off emitted none by design.

Competing hypotheses and discriminator:

- H1: The zero source payload is a task-descriptor/input-DMA property. The
  same task generation and named `data_ptr=0x80171E70`, `data_size=1` contract
  join the exact `0x1798B0 -> 0xCB0` input DMA, whose payload is zero.
- H2: The task contract is valid but the output edge is missing downstream.
  The task/DMA join is valid, while output-buffer or post-task rows show no
  corresponding destination contract.
- H3: The apparent rows cannot be joined at this scope. Positive target,
  task-lifetime, contract, and exact-DMA controls remain live, but no stable
  generation/ordinal/row key connects them.

Discriminator: one build and one target-valid logger-on run, with the existing
task-contract, task-lifetime, route, source-range, and exact-DMA controls. Add
one bounded join table keyed by task generation plus route ordinal/row, and
report counts for contract -> lifetime -> exact input-DMA -> post-task output
in that order. A complete join selects H1 or H2; positive controls with no
stable join select H3. Do not add another logger stability A/B.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3839_m5_task_contract_input_dma_join.sh

Positive controls: the logger-on arm must show `[phase]`, title origin
`0x00790400`/1024, hangar origin `0x006AB400`/512, task-contract rows, and
exact input-DMA rows, with no `[CRASH]` or `[ABORT]`. Use SIGKILL cleanup.
