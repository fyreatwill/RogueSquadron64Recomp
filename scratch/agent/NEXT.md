# Next work unit: classify the named task's output contract

HYPOTHESIS-ID: m5-task-output-contract-edge

s3839 selected the descriptor/input-DMA edge: the hangar contract
`data_ptr=0x80171E70`, size `1`, joined the exact zero-valued
`0x1798B0 -> DMEM 0xCB0` input DMA at matching task generations. Matching
image-DMA/writeback rows exist, so the next question is the output contract,
not whether a task ran.

Competing hypotheses and discriminator:

- H1: The task's ABI output fields are intentionally empty/zero, and the
  image-stage destination is a separate legitimate service writeback. The
  named task generation joins `output_buff=0`, `output_size=0` to a matching
  image-stage/writeback row whose destination is `0x1798B0`.
- H2: The ABI output contract is malformed or disconnected. The task's
  output fields are nonzero but do not match the image-stage/writeback
  destination or task generation.
- H3: The existing rows cannot be joined at the task-generation/route key.
  Positive target, task, input-DMA, and image-DMA controls remain live but
  no stable output join exists.

Discriminator: one target-valid logger-on run with the existing phase,
task-contract, task-lifetime, route, exact input-DMA, and image-stage controls.
Add one bounded table keyed by task generation and route ordinal/row, carrying
`data_ptr`, `data_size`, `output_buff`, `output_buff_size`, image-stage
destination/length, and output-DMA payload. Report contract -> input-DMA ->
image-stage -> output-DMA counts and exact destination matches. H1 is selected
by stable joins with zero ABI output fields and a matching separate
writeback; H2 by stable joins with a nonzero mismatch; H3 by live controls but
no stable join. Do not revive the alternate-family or retail object watch.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3840_m5_task_output_contract_edge.sh

Positive controls: title VI `0x00790400`/1024, hangar VI `0x006AB400`/512,
task-contract rows, exact input-DMA rows, image-stage rows, and no `[CRASH]` or
`[ABORT]`. Use SIGKILL cleanup.
