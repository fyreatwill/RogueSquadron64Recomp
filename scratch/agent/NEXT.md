# NEXT work unit (s2272) — phase-gated staggered paired route

HYPOTHESIS-ID: m5-image-output-contract-completeness

## Work unit

Run one same-build pair with the silent+C88=`0` arm launched first and the
image+C88=`0` arm launched only after the silent run log records its first
`[phase] vi_width=512` transition. Keep
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, the
reduced trace, and the existing phase/audio/image probes. The second process
still overlaps the first after the phase gate; the gate is the VI transition,
not elapsed time.

## Competing hypotheses and discriminating measurement

- **H-InitialPairContention:** silent records its first 512 phase before the
  image process starts and remains target-qualified afterward. This shows the
  immediate-launch silent failure was caused by initial paired workload
  contention; compare only target windows after both arms overlap.
- **H-SilentArmPairRoute:** silent fails before recording 512 while no image
  process has started. This selects an arm-specific route failure under the
  silent arm's paired recipe and leaves output completeness open.
- **H-LivePairContention:** silent records 512 before image launch but then
  loses target progress after image starts. This selects contention during
  overlap and leaves the image rows unpaired unless both arms later qualify.
- **H-CompleteStaggeredTarget:** both arms qualify through title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Compare every phase-10
  nonzero image-stage tuple against exact source/consumer tuples through the
  overlapping target window; otherwise keep the output contract open.

The discriminating table is
`(silent_first_512_before_image_start, silent_later_512, image_start_event,
arm, startup, missing_func, B40_rows, route_state_rows, title, hangar,
phase, width, origin, image_stage_tuple, stage_nz, source_tuple,
consumer_tuple, classification, completion_event, source_event,
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
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2272_silent_phase_gated_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2272_silent_phase_gated_pair_driver.log 2>&1 &
silent_pid=$!
while kill -0 "$silent_pid" 2>/dev/null && ! grep -q '\[phase\] vi_width=512' /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/s2272_silent_phase_gated_pair/run.log; do sleep 1; done
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2272_image_after_silent_512_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2272_image_after_silent_512_pair_driver.log 2>&1 &
image_pid=$!
wait "$silent_pid"
silent_rc=$?
wait "$image_pid"
image_rc=$?
printf 'silent_rc=%s image_rc=%s\n' "$silent_rc" "$image_rc"
```

Record the image-start event relative to the silent first-512 line, all
positive controls, both target qualifications, and every phase-10 nonzero
image tuple plus exact source/consumer join. Do not promote the image arm or
add a writeback, consumer, slot, gate, or guard change.
