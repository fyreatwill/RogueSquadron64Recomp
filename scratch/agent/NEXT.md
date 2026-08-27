# NEXT work unit (s2680) — execute M5 Step 1 same-build audio re-baseline

HYPOTHESIS-ID: m5-audio-destub-step1-contract

## Work unit

Run the existing qualified AUTOPILOT driver once with the real Factor 5 image
arm and once with `ROGUESQ_AUDIO_UCODE=0` silent control, using one build and
the same phase-gated capture. This is the M5-AUDIO-PLAN Step 1 re-baseline;
do not change behavior or add a new guard/writeback edge.

## Competing hypotheses and discriminator

- `H-AudioDegeneracy`: the image arm creates downstream service, slot, voice,
  or PCM progress that the silent arm lacks.
- `H-ContractGap`: the image arm has DMEM/DMA and completion activity but no
  additional downstream contract edge.
- `H-RouteOnly`: both arms have the same downstream rows and differ only in
  route timing or reachability.

The discriminator is one phase-keyed table containing, for both arms,
`audtask-dispatch`, task fields, DMEM/DMA, image break/exit, SP completion,
service return, slot/status transitions, voice/MORT rows, PCM source/consumer,
and title/hangar route markers. A new downstream image-only row selects
`H-AudioDegeneracy`; image-only DMEM/DMA with no downstream divergence selects
`H-ContractGap`; identical downstream rows with the same target phases select
`H-RouteOnly`. A missing positive route control invalidates the run.

## Exact commands

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run the existing AUTOPILOT capture recipe from `build/`, once with the
   default image arm and once with `ROGUESQ_AUDIO_UCODE=0`; use
   `PROBE_PHASE_WIDTH=1 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_ALL=1` plus the
   existing M5 task/PCM joins. Launch both arms in the same iteration and
   terminate each process group with SIGKILL.
3. Record the complete table and phase-gated verdict under
   `scratch/agent/s2680_m5_step1_rebaseline/`; enqueue the soak rather than
   babysitting it.
