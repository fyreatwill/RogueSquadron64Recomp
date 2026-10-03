# Next work unit: order vector stores against the zero input DMA

HYPOTHESIS-ID: m5-audio-vector-store-ordering

s3816 added vector instruction-class provenance and selected an independent RSP
vector writer, but the target source span is still zero at the input DMA.

Competing hypotheses and discriminator:

- H1: independent vector stores precede the `0xCB0 -> 0xE48` input DMA and are
  overwritten by its zero payload.
- H2: vector stores follow the input DMA, so they cannot explain the zero
  payload consumed by that DMA; the zero producer remains a DMA/initialization
  write.
- H3: sequence relation remains unobservable despite target-valid provenance.

The discriminator is one target-valid, phase-scoped sequence join covering
every writer of DMEM `0xCB0..0xE48`: vector sequence before the input-DMA
sequence selects H1, vector sequence after it selects H2, and absent/unjoinable
sequence rows selects H3. Do not repeat the existing census unchanged.

Commands:

    rg -n "m5-dmem-coverage|m5-source-range-writer|audio_dmem_dma_write" src lib/N64ModernRuntime
    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3817_m5_vector_store_ordering
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3817_m5_vector_store_ordering/image 180 1

Before building, add the single writer-sequence join at the existing DMEM
writer hook and preserve the positive controls. Inspect only bounded markers
in `run.log`; classify H1/H2/H3 from the complete target join. Do not run a
second arm. Kill any surviving game process with SIGKILL.
