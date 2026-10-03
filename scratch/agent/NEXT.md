# Next work unit: identify the upstream writer of the zero DMEM source vector

HYPOTHESIS-ID: m5-audio-zero-dmem-producer

s3813 qualified the isolated real image route through title and hangar. Its
stage-3 input DMA is live but consumes zero DMEM `0xCB0..0xE48` before writing
`0x1798B0..0x179A48`. The next unit is one batched source-producer census on
that route, retaining the independent positive controls.

Competing hypotheses and discriminator:

- H1: a guest CPU writer/fill overlaps the source object before the image task;
  a phase-scoped writer row identifies its PC and value.
- H2: no guest CPU writer overlaps it, and the zero is produced by the RSP/
  DMEM initialization or DMA path; target-valid DMEM coverage and task joins
  show the zero transition without a CPU writer.
- H3: the census is coverage-invalid despite target reachability; phase or
  whole-RDRAM controls fail, or the image arm crashes before the source join.

The discriminating measurement is the first target-valid source-DMA join with
the writer census and DMEM coverage in the same run. A CPU writer/value selects
H1; a live zero-valued RSP/DMEM chain with no overlapping CPU store selects H2;
missing controls or no target-valid join selects H3. Do not add a mitigation.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3814_m5_zero_dmem_producer
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3814_m5_zero_dmem_producer/image 180 1

Inspect bounded markers in `run.log`: title/hangar phase lines, positive
controls, source-writer/DMEM-coverage rows, `m5-input-dma`, and crash/abort.
Kill any surviving game process with SIGKILL. The source-writer census must be
phase-scoped and regeneration-safe; if its controls are not already present,
stop and treat that as H3 rather than adding a second build/run.
