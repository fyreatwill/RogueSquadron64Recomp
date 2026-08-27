# NEXT work unit (s2774) — M5 Step 1 phase-qualified same-build audio pair

HYPOTHESIS-ID: m5-step1-qualified-rebaseline

## Work unit

Run the qualified AUTOPILOT route with one compiled Debug build and two
same-build arms: the default Factor 5 image arm and `ROGUESQ_AUDIO_UCODE=0`
silent control. Keep the compiled C88 default; do not set
`ROGUESQ_M5_C88_VALUE`. Gate interpretation on title `VI 1024` and hangar
origin `0x006AB400`, and collect the existing phase-keyed task/audio/PCM
controls in both arms. This is one paired validation experiment; do not add
new instrumentation or chase a downstream null if the target phases are not
reached.

## Competing hypotheses and discriminator

- H-ImageContract: the image arm reaches both target phases and shows the
  expected nonzero image-task activity while the silent control does not.
- H-RouteInvalid: either arm fails to reach title 1024 and hangar origin, so
  no audio-contract conclusion is valid.
- H-SharedPath: both arms reach the phases and share the same task/route
  activity, which would refute the claim that the current image arm is the
  distinguishing de-stub boundary.

The discriminator is one same-build table keyed by arm and phase: target-phase
reachability, image DMEM/DMA/completion counts, silent-arm zero controls, and
PCM/service joins. Target phases in both arms make the comparison valid;
missing target phases select route-invalid and require a recipe fix before any
downstream null is interpreted.

## Exact commands

1. Use the existing qualified AUTOPILOT pair recipe, with
   `ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_AUTOPILOT`, `PROBE_PHASE_WIDTH=1024`, and
   `PROBE_KEYS_FROM_PHASE=1`; run image and silent arms concurrently from
   `build/Debug` and SIGKILL both after the recipe timeout.
2. Preserve `ROGUESQ_M5_C88_VALUE` unset, set `ROGUESQ_AUDIO_UCODE=1` only on
   the image arm and `0` only on the control, and retain the existing passive
   `ROGUESQ_LOG_ALL`/M5 join variables.
3. Compare only rows at title 1024 and hangar `0x006AB400`; write the result
   and phase validity to the next ledger entry.

Expected outcomes: qualified target phases in both arms permit the image vs
silent task/PCM comparison; absent target phases invalidate the row and select
recipe repair, not an audio hypothesis.
