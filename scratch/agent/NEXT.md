# NEXT work unit (s2271) — order-swapped paired route qualification

HYPOTHESIS-ID: m5-image-output-contract-completeness

## Work unit

Run one fresh same-build pair with the silent+C88=`0` arm launched first and
the image+C88=`0` arm launched second. Keep the qualified
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`
route, reduced trace, and phase gates. This tests whether s2270's image-first
route failure is launch-order-sensitive before using any image rows for an
output-contract comparison.

## Competing hypotheses and discriminating measurement

- **H-LaunchOrderSensitive:** silent-first reaches 1024/title/hangar while the
  image-first s2270 pair had no silent target window. This selects launch-order
  route sensitivity; do not compare unpaired image rows.
- **H-OrderIndependentRoute:** silent-first also times out before 1024 after
  the positive controls. This selects route sensitivity independent of launch
  order and leaves output completeness open.
- **H-CompletePairedTarget:** both arms qualify through title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Then compare every
  phase-10 nonzero image-stage `(dest,len,FNV,nz)` tuple against exact source
  and consumer tuples through the target window.
- **H-MixedOrLateContract:** both arms qualify and the target comparison either
  repeats the s2268 exact join plus unmatched nonzero row (mixed contract) or
  joins the formerly unmatched row later with `ordering_violation=0` (late
  delivery).

The discriminating table is
`(launch_order, arm, startup, missing_func, B40_rows, route_state_rows,
title, hangar, phase, width, origin, image_stage_tuple, stage_nz,
source_tuple, consumer_tuple, classification, completion_event, source_event,
consumer_event, ordering_violation, pcm_fnv, pcm_nz, driver_outcome,
crash_or_timeout, crash_pc, last_guest_pc)`. Positive controls are startup,
one `[missing-func]`, B40 rows, route-state rows, and the 1024/title/hangar
transitions in each arm.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2271_silent_first_c88_0_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2271_silent_first_c88_0_pair_driver.log 2>&1 &
silent_pid=$!
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2271_image_second_c88_0_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2271_image_second_c88_0_pair_driver.log 2>&1 &
image_pid=$!
wait "$silent_pid"
silent_rc=$?
wait "$image_pid"
image_rc=$?
printf 'silent_rc=%s image_rc=%s\n' "$silent_rc" "$image_rc"
```

Record both driver outcomes, all positive controls, target qualification,
every phase-10 nonzero image tuple and exact source/consumer join, completion
order, and the silent all-zero PCM control. Do not promote the image arm or
add a writeback, consumer, slot, gate, or guard change.
