# NEXT work unit (s2968)

HYPOTHESIS-ID: m5-audio-step1-image-vs-silent

## Unit

Execute M5 plan Step 1: same-build, phase-gated comparison of the Factor 5
audio image arm and the explicit silent `musyx_stub` control. This is one
experiment with both arms, not two sequential iterations. Use the existing
AUTOPILOT route and retain all passive breadcrumb instruments. Do not change
audio behavior or add a new diagnostic field.

## Competing hypotheses and discriminator

- H-AudioDegeneracy: the silent path causes downstream wait/slot/voice/PCM
  failures. The image arm should add the predicted service, slot, voice, or
  PCM transition while preserving the same route.
- H-ContractGap: the image runs and completes but its task/DMEM/DMA/output
  contract is incomplete. The image arm should show dispatch, task fields,
  DMEM/DMA, image exit, and SP completion, but fail to close a downstream
  service/slot/voice/PCM join.
- H-MixedPipelines: RSP image audio and CPU MORT speech are independent. The
  two arms may have identical RSP rows while MORT descriptor/PCM rows diverge
  independently.

The discriminating measurement is one phase-keyed row for each arm containing
`M_AUDTASK` dispatch/exit, task fields and source hash, DMEM change and DMA
ranges, image completion, SP completion, service entry/return, status/slot
transitions, voice/reap activity, MORT descriptor class, PCM source/consumer
joins, and VI route phase (`1024 @ 0x00790400`, `512 @ 0x006AB400`). A whole-
RDRAM oracle positive control and the port route/phase control must both fire;
pre-title nulls are unevaluable.

## Commands

1. Build one binary:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
2. From `build/Debug`, launch both arms concurrently with the same
   `ROGUESQ_AUTOPILOT`, `ROGUESQ_LOG_ALL`, `PROBE_PHASE_WIDTH=1`, and
   `PROBE_KEYS_FROM_PHASE=1` settings; use `ROGUESQ_AUDIO_UCODE=0` for the
   silent arm and `ROGUESQ_AUDIO_UCODE=1` for the image arm. Capture each arm
   to a non-dot final path, watchdog it, and SIGKILL the process group.
3. Check the whole-RDRAM oracle control before interpreting narrow retail or
   port nulls; summarize both arms in one phase-keyed table.

Expected outcomes: image-only downstream progress selects H-AudioDegeneracy;
image DMEM/DMA/SP progress without service/slot/PCM closure selects
H-ContractGap; matching RSP rows with independent MORT/PCM divergence selects
H-MixedPipelines. Rollback/control is `ROGUESQ_AUDIO_UCODE=0`; no source
change is authorized by a route-only difference.
