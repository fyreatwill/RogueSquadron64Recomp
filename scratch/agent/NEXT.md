# Next work unit: rerun the upstream zero-DMEM producer census with its gates armed

HYPOTHESIS-ID: m5-audio-zero-dmem-producer

s3814 reached title and hangar with 22,850 target input-DMA rows, but the
requested source-writer/DMEM census was not enabled. It is coverage-invalid;
do not infer a producer from its zero payload.

Competing hypotheses and discriminator:

- H1: a guest CPU writer/fill overlaps the source object before the image task;
  a phase-scoped writer row identifies its PC and value.
- H2: no guest CPU writer overlaps it, and the zero is produced by the RSP/
  DMEM initialization or DMA path; live DMEM coverage and source-transition
  rows show the zero transition without a CPU writer.
- H3: the corrected census remains coverage-invalid despite target reachability;
  its positive census controls or target-valid joins are absent.

The discriminating measurement is the first target-valid source-DMA join in the
same run as the writer, RSP-source, and source-transition controls. A CPU
writer/value selects H1; a live zero-valued RSP/DMEM chain with no overlapping
CPU store selects H2; missing controls or target joins selects H3.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3815_m5_zero_dmem_producer
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3815_m5_zero_dmem_producer/image 180 1

Inspect bounded markers in `run.log`: phase/title/hangar lines, census
controls, `m5-source-range-reader`, `m5-dmem-coverage`,
`m5-source-range-writer`, `m5-source-transition`, `m5-input-dma`, and
crash/abort. Do not run a second arm or add instrumentation if the controls
are absent; classify H3. Kill any surviving game process with SIGKILL.
