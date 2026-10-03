# Next work unit: qualify an isolated image arm for the zero-DMEM producer

HYPOTHESIS-ID: m5-audio-image-arm-stability

s3811 and s3812 tested opposite launch orderings with an explicit silent arm.
Image failed before target at guest PC `0x8000834C` in both; silent reached
title/hangar. Launch-order interaction is closed. The next bounded unit must
qualify one image arm to target before returning to the zero-DMEM producer.

Competing hypotheses and discriminator:

- H1: a single image arm reaches title and hangar, enabling the source-producer
  census.
- H2: image remains pre-target even when isolated, so startup needs a new
  discriminator before boundary work can resume.
- H3: image reaches target but its joined source/DMA rows remain zero,
  selecting the upstream producer boundary directly.

The discriminating measurement is one same-build image-only run with the
minimal phase/task-contract/audio-return/route controls and the independent
whole-RDRAM positive control. Select H1 if image reaches title and hangar;
select H2 if it still fails at `0x8000834C`; select H3 only if target-valid
image source/DMA rows join and expose a nonzero-versus-zero producer split.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s3813_m5_image_isolated_qualification
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_AUTOPILOT='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3813_m5_image_isolated_qualification/image 180 1

Compare `run.log` for title/hangar phase, task-contract/audio-return/route
rows, and `[CRASH]`/`[ABORT]`; kill any surviving game process with SIGKILL.
