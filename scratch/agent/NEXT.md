# Next work unit: image-first minimal qualification of the DMEM task-data boundary

HYPOTHESIS-ID: m5-audio-dmem-boundary-launch-order

s3811 removed the legacy diagnostic bundle, but the corrected image arm still
crashed 36 times at guest PC `0x8000834C` before any task-contract,
audio-return, route, or target-VI row. The concurrently launched silent arm
reached title and hangar. Test whether the launch order is the remaining
startup discriminator before judging the final DMEM task-data byte.

Competing hypotheses and discriminator:

- H1: launch-order interaction is causal; starting image first makes image
  target-valid or moves the pre-target failure to silent.
- H2: image startup failure is deterministic and independent of launch order;
  image still fails before target while silent remains target-valid.
- H3: the corrected task-data boundary is consumed, but it cannot be selected
  until an image arm reaches target and differs in a joined task/DMA/service/PCM
  row.

The discriminating measurement is one same-build concurrent run with image
started first and explicit silent started second, retaining only phase,
task-contract, audio-return, route, and no-crash controls. Select H1 if the
failing arm swaps or image reaches a target VI; select H2 if image again fails
at `0x8000834C` before target while silent reaches hangar; select H3 only if
image reaches target and its joined rows differ from silent.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3812_m5_image_first_boundary_pair
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3812_m5_image_first_boundary_pair/image 180 1 > scratch/agent/s3812_m5_image_first_boundary_pair/image.driver.log 2>&1 & p1=$!
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3812_m5_image_first_boundary_pair/silent 180 1 > scratch/agent/s3812_m5_image_first_boundary_pair/silent.driver.log 2>&1 & p2=$!
    wait "$p1"; wait "$p2"

Compare each `run.log` for title/hangar phase, task-contract/audio-return/
route rows, and `[CRASH]`/`[ABORT]`. Kill surviving game processes with
SIGKILL after both arms reach hangar or one arm fails before target.
