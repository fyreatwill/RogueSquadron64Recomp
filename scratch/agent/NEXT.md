# Next work unit: qualify retail/port task-field parity

HYPOTHESIS-ID: m5-task-output-contract-parity

s3840 selected the port-side empty-ABI/separate-writeback result: 458 named
port task rows had `output_buff=0` and `output_buff_size=0`; 452/458 stage
generations joined the `0x1798B0`/`0x198` output DMA. The next bounded unit is
one paired target-valid retail-oracle/port capture using the existing positive
controls, comparing the same named task fields and task-generation/output-DMA
destination class.

Competing hypotheses and discriminator:

- H1: Retail also leaves ABI output fields zero and uses the separate
  `0x1798B0` writeback edge. Select if retail target-phase task rows have zero
  output fields and the named output-DMA/writeback class matches port.
- H2: Retail populates a nonzero ABI output field that the port loses. Select
  if retail target-phase rows have a stable nonzero output field while port
  rows remain zero, with positive whole-RDRAM and target-VI controls.
- H3: The retail task rows cannot be joined to the named target phase or the
  existing oracle capture is pre-target. Select only if controls are live but
  no stable target-phase task-field join exists.

Discriminator: one table keyed by target VI phase and task data pointer/size,
containing retail task pointer, output fields, data fields, and output-DMA or
writeback destination; compare it with the s3840 port table. A null is invalid
unless whole-RDRAM, retail target-VI, port target-VI, and port task controls all
fire.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3841_m5_task_output_contract_parity.sh

Use `PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1`, keep the existing
task/image/route controls, run from `build/`, and SIGKILL the game/process
group after title 1024 and hangar 512 are captured. Do not add a writeback
guard or change task dispatch based on the s3840 result.
