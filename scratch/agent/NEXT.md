# Next work unit: attribute the zero source-RDRAM span

HYPOTHESIS-ID: m5-audio-source-rdram-writer

s3817 qualified the DMEM ordering join. The target-valid image route reached
title and hangar; 512/512 sampled `0xCB0`-window vector rows and 4,096/4,096
broader `0xDxx` vector rows occurred after the `0xCB0 -> 0xE48` input DMA.
Do not repeat the DMEM census.

Competing hypotheses and discriminator:

- H1: the zero source span is written by a legitimate CPU clear/fill before
  the input DMA.
- H2: the source span is zero because of a distinct DMA/RDRAM writer or stale
  source object, not the known clear path.
- H3: the target-phase source-RDRAM writer cannot be joined to the input DMA.

The discriminator is one target-valid, phase-scoped RDRAM writer join covering
`0x1798B0..0x179A48`, with the whole-RDRAM/phase/task controls preserved.
Identify the final writer PC and store width/value immediately before the
input DMA. A legitimate zero-valued clear/fill selects H1; a distinct writer
or object selects H2; absent or unjoinable writer evidence selects H3.

Before building, enumerate the existing `m5-input-writer` and RDRAM-store
hooks and add only the sequence join needed to relate their last writer to the
input-DMA event. Build once, then run one isolated image arm:

    rg -n "m5-input-writer|pre_dma_writer|source_range_dma_write|1798B0" src/main/main.cpp lib/N64ModernRuntime
    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3818_m5_source_rdram_writer
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 ROGUESQ_LOG_M5_INPUT_WRITER=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3818_m5_source_rdram_writer/image 180 1

Inspect bounded phase/control/input-writer markers only. Kill any surviving
game process with SIGKILL.
