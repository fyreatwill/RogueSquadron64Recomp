# Next work unit: attribute the zero DMEM vector writer

HYPOTHESIS-ID: m5-audio-zero-dmem-vector-origin

s3815 qualified the census and selected the RSP/DMEM/DMA chain at route scope,
but `kind=vector` rows still do not identify whether they are an independent
RSP vector fill or bookkeeping around the preceding zero DMA.

Competing hypotheses and discriminator:

- H1: an RSP vector instruction independently writes the zero source vector;
  a provenance field joins the vector write to an RSP task/PC or instruction
  class before the stage-3 input DMA.
- H2: the vector rows are derived from the preceding zero DMA, with no
  independent vector producer; the same-run writer join shows DMA ancestry and
  no intervening write.
- H3: provenance remains unobservable even with the existing positive controls;
  the target-valid join or writer attribution is missing.

The discriminator is one target-valid, phase-scoped provenance join covering
every writer of DMEM `0xCB0..0xE48`: independent RSP/vector provenance selects
H1, DMA ancestry with no intervening write selects H2, and absent controls or
unjoinable rows selects H3. Do not repeat the existing census unchanged.

Commands:

    rg -n "m5-dmem-coverage|kind=vector|source-range-writer|DMEM" src lib/N64ModernRuntime lib/rt64
    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3816_m5_zero_dmem_vector_origin
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3816_m5_zero_dmem_vector_origin/image 180 1

Before building, add the single provenance field at the existing DMEM writer
hook and preserve the positive controls. Inspect only bounded markers in
`run.log`; classify H1/H2/H3 from the complete target join. Do not run a
second arm. Kill any surviving game process with SIGKILL.
