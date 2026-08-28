# NEXT work unit — M5 Step-1 image/silent qualification at title and hangar

HYPOTHESIS-ID: m5-audio-step1-contract-qualification

## Competing hypotheses and discriminator

- H-AudioDegeneracy: the silent path is responsible for a downstream wait,
  slot, voice, or PCM failure; the image arm should add the predicted edge.
- H-ContractGap: the image executes but its task/DMEM/DMA/output contract is
  incomplete; image-only activity will fail to close a later join.
- H-MixedPipelines: Factor 5 RSP audio and CPU MORT speech are independent;
  one can progress while the other remains absent.
- H-RouteFailure: a run that never reaches title/hangar makes every downstream
  audio null unevaluable; the validated route should be present in this unit.

The discriminator is one phase-keyed table for both arms in one build/run:
whole-RDRAM/oracle control and route phase; M_AUDTASK dispatch and task fields;
DMEM/DMA and image break/`Broke`; SP completion; guest service and slot/voice
transitions; MORT class; and PCM source/consumer joins. If title/hangar is
absent, RouteFailure is selected and downstream audio is unevaluable. If the
image has DMEM/DMA plus completion but no later join, ContractGap is selected.
If MORT and RSP rows progress independently, MixedPipelines is selected. A
silent/image difference only selects AudioDegeneracy when it includes the
predicted downstream edge, not merely a return counter.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp -- -j2
    env ROGUESQ_AUTOPILOT=1 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_ALL=1 \
      PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_PHASE_TIMEOUT=180 \
      PROBE_LEAVE_OK=1 zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh

The script must launch both image and silent arms from the same build and
retain the independent oracle positive control. Write the phase-keyed result
under `scratch/agent/s3039_m5_step1_contract_pair/`; do not change a gate,
wait, voice guard, or output destination from this qualification alone.
