# NEXT work unit (s2244) — measure no-log baseline divergence

HYPOTHESIS-ID: m5-image-prephase-crash-discriminator

## Work unit

Run one same-build concurrent two-arm baseline using the qualified image arm
with M5 logging disabled in both processes. Keep the functional environment,
route, phase gate, timeout, and watchdog identical. This tests whether the
s2243 divergence is present without the logging arm. No build, oracle watch,
code change, or new instrument is needed.

## Competing hypotheses and discriminator

- **H-NoLogStablePrePhase:** both no-log arms reach the common 640 route and
  stop before 1024 at `fillSampleStreamRange+8136` with
  `last-guest-pc=0x8000b650`. This establishes a stable no-log baseline and
  makes logging the next isolation variable, but does not yet prove that
  logging caused s2243 arm A's RT64 crash.
- **H-BaselineNondeterminism:** the two identical no-log arms diverge in crash
  PC, last guest PC, or phase progression. This confirms baseline
  nondeterminism and blocks logging or field348 inference at this scope.
- **H-NoLogIntermittentQualification:** both no-log arms reach title `1024 @
  0x00790400` and hangar `512 @ 0x006AB400`. The pre-phase crash is
  intermittent under this recipe; resume the field348 census only with a
  fresh unit and qualified target rows.
- **H-RouteControlInvalid:** either arm lacks the common startup/640 route
  controls or has a different functional environment. The comparison is
  invalid and selects no crash explanation.

The discriminating table is keyed by
`(arm,phase,width,origin,driver_rc,missing_func_count,crash_pc,last_guest_pc)`.
The positive controls are the startup markers, 640 at
`0x00696100`, matching functional env, and, for a successful arm, title 1024
and hangar 512. Matching no-log failures, divergent no-log failures, and
both-arm target qualification select the three substantive hypotheses above.

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2244_image_crash_nolog_a 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2244_image_crash_nolog_a_driver.log 2>&1 &
pid_a=$!
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2244_image_crash_nolog_b 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2244_image_crash_nolog_b_driver.log 2>&1 &
pid_b=$!
wait "$pid_a"; rc_a=$?
wait "$pid_b"; rc_b=$?
printf 'arm_a=%s arm_b=%s\n' "$rc_a" "$rc_b"
```

Compare only the bounded driver tails and exact phase/crash/control counts
from `scratch/s73_post_a_scene/s2244_image_crash_nolog_a/run.log` and
`scratch/s73_post_a_scene/s2244_image_crash_nolog_b/run.log`. If either arm
misses the 640 control, treat the A/B as invalid. Do not infer field348
writers from a run that misses both target phase markers.
