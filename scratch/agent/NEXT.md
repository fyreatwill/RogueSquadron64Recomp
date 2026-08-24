# NEXT work unit (s2219) — validate the opt-in Factor 5 audio arm

HYPOTHESIS-ID: m5-audio-image-arm-validation

## Work unit

Execute step 2 of `docs/M5-AUDIO-PLAN.md` only. Use one build and run the
silent `musyx_stub` control and `ROGUESQ_AUDIO_UCODE=1` treatment from the
same phase schedule. Keep the arm opt-in; do not flip the guest gate, remove
wait/slot/voice guards, change task fields, or enable stock `aspMain`.

The prior retail ground-truth run passed its whole-RDRAM control and found
active `0x14974C` writes, but it did not identify that word's writer or print
gate store payloads. Those are not reasons to add an instrument before this
step: the existing arm validation has a complete port-side discriminator.

Competing hypotheses and the single discriminator:

- H-ImageExec: the image arm executes the selected Factor 5 image and returns
  normally; its phase-keyed rows show `real_ucode=1`, a completed RSP task,
  changed DMEM/output or DMA evidence, and a valid slot transition.
- H-StubEquivalent: the image arm is still observationally equivalent to the
  silent stub at this route; dispatch/return may differ, but no valid slot
  transition or nonzero PCM appears in the treatment.
- H-ImageRouteRegress: the image arm changes route admission or stability;
  its positive phase control is present but it stalls, crashes, loses a
  later phase, or corrupts the existing task/DMEM contract compared with the
  same-build control.
- H-Coverage: a positive all-width/phase prefix or the treatment's dispatch
  rows are absent, so any image-arm null is unevaluable.

The discriminator is one phase-keyed control/treatment table containing the
positive prefix, 640/title/hangar phase rows, `audtask-dispatch` and
`RspExitReason`, host canary status, DMEM/output/DMA rows, slot status
transitions, and `pcm-sanity` nonzero/all-zero counts. H-ImageExec requires
the treatment execution/return plus valid output and slot evidence;
H-StubEquivalent requires matched coverage and no valid output/slot/PCM;
H-ImageRouteRegress requires matched early coverage with a treatment-only
route or stability failure; and H-Coverage wins if the same-run controls are
missing. A dispatch counter alone is not a positive control.

## Exact commands

Build once from the repository root:

~~~sh
cmake --build build --config Debug --target RogueSquadron64Recomp
~~~

Run the existing eleven-Start driver for the treatment, with all passive M5
diagnostics armed:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 \
  ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh \
  m5-audio-step2 30 12 > scratch/agent/s2219_image_arm.log 2>&1
~~~

Run the unset-env control from the same built binary and schedule:

~~~sh
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 \
  ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh \
  m5-audio-step2-control 30 12 > scratch/agent/s2219_stub_control.log 2>&1
~~~

Use SIGKILL for any watchdog termination. Inspect only the phase-keyed table
above, plus `[CRASH]`/`[ABORT]` markers and the final phase; do not treat a
timeout or all-zero PCM as success.
