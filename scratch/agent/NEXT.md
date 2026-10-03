# Next work unit: attribute the exact retail image-stage destination

HYPOTHESIS-ID: m5-task-output-contract-retail-parity

The target-valid s3846 capture selected the shared destination role at bounded
scope: retail uses `data_ptr=0x80173CB0`, has 120,550 writes in its task span,
and 930,770 writes in candidate image-stage `0x167000..0x16C000`; port has
2,964 joined image-DMA rows. The retail destination watch is broad and is not
yet an exact task-generation join.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: the retail task generation reaches the same image-stage destination role
  as port, with a repeatable task-to-writer attribution.
- H2: retail writes in the broad candidate range are unrelated activity; no
  task-generation-correlated stage writer exists.
- H3: the broad watch cannot be made phase/task-correlated without losing a
  required positive control, so the exact join is not measurable by this arm.

Discriminating measurement: one paired run with the existing validated port
controls and oracle whole-RDRAM control, title/hangar VI phase gates,
`--pc-task-dump 0x80033FCC --pc-task-type 2`, phase-scoped writer-PC
histograms for the exact candidate destination watch, and port
`audtask-image-stage`/`audtask-image-dma-join` rows. H1 requires a stable
retail writer attribution during the task rows that matches the port stage
destination role and length; H2 requires positive retail task/phase controls
but no phase-correlated writer; H3 requires a missing control or an
unresolvable watch budget.

Use `scratch/agent/run_s3844_m5_task_output_contract_retail.sh` as the starting
recipe, replacing the broad `0x167000..0x16C000` watch with the exact
phase-scoped candidate range and adding the oracle's phase histogram for that
watch. Keep the drain-in-loop control that made s3844/s3846 target-valid. Do
not add a writeback guard or infer a destination from the port address. The
M3 heap-span validation remains blocked on the absent MIPS toolchain and is
not this unit.

Maintenance session 3845 compacted CURRENT-TRUTH; no experiment was run.
