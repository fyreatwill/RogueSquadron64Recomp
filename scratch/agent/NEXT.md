# NEXT work unit (s2269) — image-stage completeness repeat

HYPOTHESIS-ID: m5-image-output-contract-completeness

## Work unit

Run one same-build image+C88=`0` / silent+C88=`0` pair with the qualified
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`
route. Use the existing reduced trace and image-stage/PCM joiners. Both arms
must pass startup, one `[missing-func]`, B40/route-state controls, title
`1024 @ 0x00790400`, and hangar `512 @ 0x006AB400` before interpreting phase
10 output. This is a contract-completeness experiment, not a mitigation.

## Competing hypotheses and discriminating measurement

- **H-MixedContractStable:** the image arm again has a nonzero phase-10 row
  with exact source and consumer joins plus a second nonzero row that remains
  unmatched. This selects a mixed image-output contract at the measured
  stage rows.
- **H-LateDelivery:** the second nonzero phase-10 row from s2268 receives an
  exact source and consumer join later in the same qualified capture, with no
  `ordering_violation`. This selects late delivery or join timing as the
  explanation for the prior unmatched row.
- **H-NonrepeatableStage:** the image arm reaches the target phases but the
  phase-10 nonzero tuple set changes or the prior second row disappears. This
  selects route-sensitive/nonrepeatable observation and keeps completeness
  open; it does not authorize a guard.
- **H-PairRouteInvalid:** either arm misses any required control or target
  phase, or exits before the comparison window. This selects route work only.

The discriminating table is
`(arm, startup, missing_func, B40_rows, route_state_rows, title, hangar,
phase, width, origin, image_stage_tuple, stage_nz, source_tuple,
consumer_tuple, classification, completion_event, source_event,
consumer_event, ordering_violation, pcm_fnv, pcm_nz, driver_outcome,
crash_or_timeout, crash_pc, last_guest_pc)`. For each phase-10 nonzero image
row, compare exact `(dest,len,FNV,nz)` tuples against source and consumer
records through the end of the target window. Positive controls are the
startup marker, one `[missing-func]`, B40 rows, route-state rows, and title
and hangar phase transitions in both arms.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2269_image_c88_0_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2269_image_c88_0_pair_driver.log 2>&1 &
image_pid=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2269_silent_c88_0_pair 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2269_silent_c88_0_pair_driver.log 2>&1 &
silent_pid=$!
wait "$image_pid"
image_rc=$?
wait "$silent_pid"
silent_rc=$?
printf 'image_rc=%s silent_rc=%s\n' "$image_rc" "$silent_rc"
```

Record both driver outcomes, controls, title/hangar qualification, every
phase-10 nonzero image tuple, exact source/consumer joins, completion order,
and the silent all-zero PCM control. Do not promote the image arm or add a
writeback, consumer, slot, gate, or guard change.
