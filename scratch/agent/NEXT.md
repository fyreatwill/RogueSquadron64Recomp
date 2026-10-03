# Next work unit: join the retail task descriptor to its actual image destination

HYPOTHESIS-ID: m5-task-output-contract-retail-parity

The paired target-valid s3844 capture selected parity for empty ABI output
fields, but retail uses `data_ptr=0x80173CB0` while port uses
`0x80171E70`. The retail watch of port's `0x1798B0..0x179A48` span had no
hits, so the separate-edge contract is not yet qualified across both arms.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: retail's `0x80173CB0` task generation reaches a separate image-stage /
  writeback destination, matching the port's separate service edge.
- H2: retail's task generation has no corresponding image-stage/writeback edge,
  so the port's edge is a port-only behavior.
- H3: either arm lacks whole-RDRAM or both target-VI controls, making the join
  coverage-invalid rather than informative.

Discriminating measurement: one paired run with the existing validated port
controls and the oracle's whole-RDRAM control, title/hangar VI phase gates,
`--pc-task-dump 0x80033FCC --pc-task-type 2`, a retail physical watch over the
retail descriptor's candidate source/output region, and port
`audtask-image-stage`/`audtask-image-dma-join` rows. Join by task generation and
compare stage destination, length, and payload. H1 requires matched stage /
writeback evidence on both arms; H2 requires positive retail task and phase
controls but no matching edge; H3 requires a missing control or target phase.

Use `scratch/agent/run_s3844_m5_task_output_contract_retail.sh` as the starting
recipe, updating only the retail watch range after identifying it from the
task-generation evidence. Keep the drain-in-loop control that made s3844
target-valid. Do not add a writeback guard or infer a destination from the
port address. The M3 heap-span validation remains blocked on the absent MIPS
toolchain and is not this unit.

Maintenance session 3845 compacted CURRENT-TRUTH; no experiment was run.
