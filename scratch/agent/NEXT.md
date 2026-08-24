# NEXT work unit (s2243) — distinguish logging amplification from the image-arm crash

HYPOTHESIS-ID: m5-image-prephase-crash-discriminator

## Work unit

Run one same-build A/B concurrently, using the qualified image arm in both
processes. Arm A keeps the full s2242 M5 logging set; Arm B keeps the same
functional environment but disables all M5 logging. No code, build, oracle
watch, or new instrument is needed. A run is valid only if its route markers
and process outcome are captured; do not infer any field348 writer result from
a run that misses both target phase markers.

## Competing hypotheses and discriminator

- **H-LoggingAmplifiedCrash:** Arm A dies before 1024 at
  `fillSampleStreamRange+8136`, while Arm B reaches 1024 and 512 with the
  route controls intact. The M5 logging footprint is sufficient to select the
  pre-phase failure split.
- **H-ImageArmIntrinsicCrash:** Both arms die before 1024 at the same
  `fillSampleStreamRange+8136` class with the same last guest PC and neither
  has target controls. Logging is not the cause at this scope.
- **H-RunNondeterminism:** The two arms have divergent pre-phase outcomes
  (different crash PCs, one target route without a logging-correlated split,
  or inconsistent phase progression). The comparison is nondeterministic and
  selects no writer or logging explanation.
- **H-RouteControlInvalid:** either arm lacks the common startup/640 route
  controls or has a different functional environment; the A/B is invalid and
  must not be interpreted.

The discriminating table is keyed by
`(arm,phase,width,origin,missing_func_count,crash_pc,last_guest_pc,
abi_rows,dma_rows,image_stage_rows,pcm_rows)`. Positive controls are the
common qualified functional env, the startup/640 phase markers, and, for a
successful arm, title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`.
The outcome that splits the hypotheses is whether only the full-logging arm
fails, both arms fail at the same PC, or the arms diverge without a logging
correlation.

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2243_image_crash_logs_on 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2243_image_crash_logs_on_driver.log 2>&1 &
pid_a=$!
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2243_image_crash_logs_off 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2243_image_crash_logs_off_driver.log 2>&1 &
pid_b=$!
wait "$pid_a"; rc_a=$?
wait "$pid_b"; rc_b=$?
printf 'arm_a=%s arm_b=%s\n' "$rc_a" "$rc_b"
```

Compare only the bounded driver tails and phase/crash/control counts from
`scratch/s73_post_a_scene/s2243_image_crash_logs_on/run.log` and
`scratch/s73_post_a_scene/s2243_image_crash_logs_off/run.log`. If both arms
reach the targets, resume the field348 census with a fresh planned unit; do
not silently fold that census into this A/B.
