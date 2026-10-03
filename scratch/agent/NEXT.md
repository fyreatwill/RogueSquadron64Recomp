# Next work unit: minimal concurrent qualification of the DMEM task-data boundary

HYPOTHESIS-ID: m5-audio-dmem-boundary-minimal-pair

The runtime stages the complete declared DMEM task-data window through `0x0F7F`;
the previous length `0xF80 - 1` omitted the final byte immediately before the
OSTask area at `0x0FC0`. The legacy validation driver crashed its corrected
image arm before target, so its diagnostic load must be removed before judging
the byte.

Competing hypotheses and discriminator:

- H1: the missing final DMEM task-data byte is part of the audio task contract;
  the corrected image arm changes a joined task/DMA/service/PCM row without
  losing the validated route.
- H2: the byte is padding or otherwise unused; image and silent controls retain
  identical downstream behavior and the corrected byte is never consumed.
- H3: the legacy diagnostic bundle, rather than the byte, destabilizes image
  startup; the minimal corrected image arm fails before target or becomes
  qualified only after the bundle is removed.

The discriminating measurement is one same-build concurrent run with default
image and explicit silent control, retaining only phase, task-contract,
audio-return, route, and no-crash controls. Select H1 only if corrected image
reaches title/hangar and shows a joined task-contract or downstream difference;
select H2 if it is route-equivalent with the positive controls; select H3 if
image still fails before target.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3811_m5_minimal_boundary_pair
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3811_m5_minimal_boundary_pair/silent 180 1 > scratch/agent/s3811_m5_minimal_boundary_pair/silent.driver.log 2>&1 & p1=$!
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3811_m5_minimal_boundary_pair/image 180 1 > scratch/agent/s3811_m5_minimal_boundary_pair/image.driver.log 2>&1 & p2=$!
    wait "$p1"; wait "$p2"

Compare each `run.log` for title/hangar phase, task-contract/audio-return/route
rows, and `[CRASH]`/`[ABORT]`. Kill surviving game processes with SIGKILL
after both arms reach hangar or one arm fails before target.
