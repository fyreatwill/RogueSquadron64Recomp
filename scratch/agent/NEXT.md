# NEXT work unit (s2245) — repeat no-log baseline through hangar

HYPOTHESIS-ID: m5-image-prephase-crash-discriminator

## Work unit

Run one same-build concurrent two-arm baseline with the qualified image arm
and M5 logging disabled in both processes. Let both drivers continue through
the title/hangar route; do not stop the surviving arm merely because it has
reached title. Use the same functional environment, phase gate, and route
controls as s2244. This is one repeat of the selected baseline-nondeterminism
test, not field348 instrumentation.

## Competing hypotheses and discriminator

- **H-RepeatedBaselineSplit:** both arms pass 640 but split again, with one
  pre-phase crash and the other reaching title or hangar. This supports
  baseline nondeterminism and keeps field348 inference parked.
- **H-NoLogStablePrePhase:** both arms pass 640 and fail before 1024 at the
  same crash PC/guest PC. This makes a stable no-log baseline plausible and
  selects a logging-enabled A/B as the next isolation variable.
- **H-NoLogTargetQualification:** both arms pass 640, reach title
  `1024 @ 0x00790400`, and reach hangar `512 @ 0x006AB400`. This classifies
  the prior failures as intermittent and permits the five-store field348
  producer census to resume.
- **H-RouteControlInvalid:** either arm lacks the common startup/640 controls
  or has a different functional environment. The A/B selects no crash
  explanation.

The discriminating table is keyed by
`(arm,640_control,title_control,hangar_control,driver_termination,crash_pc,last_guest_pc)`.
Positive controls are the common startup markers, one `[missing-func]` marker,
and the exact 640 route marker. Do not infer field348 writers from an arm that
misses the 640 control or from a run killed before its phase table is fixed.

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2245_image_crash_nolog_a 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2245_image_crash_nolog_a_driver.log 2>&1 &
pid_a=$!
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2245_image_crash_nolog_b 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2245_image_crash_nolog_b_driver.log 2>&1 &
pid_b=$!
wait "$pid_a"; rc_a=$?
wait "$pid_b"; rc_b=$?
printf 'arm_a=%s arm_b=%s\n' "$rc_a" "$rc_b"
```

Compare only bounded driver tails and exact phase/crash/control counts from
the two `run.log` files. If a driver or game remains alive after the route
table is determined, terminate the identified process group with SIGKILL;
never use SIGTERM. Record forced termination separately from a driver exit.
