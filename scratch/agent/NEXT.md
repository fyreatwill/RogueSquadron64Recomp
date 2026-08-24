# NEXT work unit (s2261) — same-build image/PCM boundary join

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent image+C88=`0` / silent+C88=`0` pair with the
qualified spin/LLE route. Launch the image arm first and the silent arm one
second later. Keep `ROGUESQ_LOG_AUDIO_RETURN=1` enabled in both arms so the
image-stage route identity is armed. Add only
`ROGUESQ_LOG_PCM_BOUNDARY=1`; continue omitting task-contract/ABI/DMA,
host-boundary, B40-read, and thread-resume tracing. Keep the image arm opt-in
and make no runtime or default change.

## Competing hypotheses and discriminator

- **H-StagePcmJoin:** both arms qualify title/hangar; the image arm repeats
  target stage rows and at least one stage row exactly matches a phase-keyed
  PCM source or consumer by destination, length, full-span FNV, nonzero count,
  and completion/source/consumer order. The output boundary reaches a
  validated PCM edge.
- **H-StageNoPcmJoin:** both arms qualify title/hangar and the image arm has
  stage rows, including the known nonzero hangar rows, but no exact PCM source
  or consumer match. This places the open edge between generated image DMA
  output and the PCM boundary, without authorizing a writeback or consumer
  guard.
- **H-PcmWithoutStage:** target PCM source/consumer rows fire but the image
  arm has no target stage rows or no nonzero stage rows. This would move the
  discriminator to stage logging/route identity or a transform contract;
  treat a missing title/hangar as invalid until controls fire.
- **H-PairRouteInvalid:** either arm fails before title/hangar after the
  startup, `[missing-func]`, 640, B40, and route-state controls. Record the
  terminal identity and do not interpret stage or PCM nulls.

The discriminator is the complete same-run table keyed by
`(arm,audio_mode,phase,width,origin,stage_rows,nonzero_stage_rows,stage_source_matches,stage_consumer_matches,pcm_source_rows,pcm_consumer_rows,exact_dest_len_fnv_nz,ordering,stable_title,hangar,driver_outcome,crash_or_timeout)`.
Positive controls are startup, one `[missing-func]`, both 640 origins, and
B40/route-state rows in each arm. Compare only target-phase rows from this
run. A route-qualified image stage with no PCM match is a boundary result,
not permission to add a mitigation.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
(
  env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2261_image_c88_0_pcm 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2261_image_c88_0_pcm_driver.log 2>&1 &
  p_image=$!
  sleep 1
  env ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2261_silent_c88_0_pcm 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2261_silent_c88_0_pcm_driver.log 2>&1 &
  p_silent=$!
  wait "$p_image"; r_image=$?
  wait "$p_silent"; r_silent=$?
  print "image_rc=$r_image silent_rc=$r_silent"
)
```

Record both driver outcomes, every 640/1024/512 phase row, B40/route-state
controls, image-stage summaries/joins, and PCM source/consumer rows. Do not
promote the image arm or add a writeback/consumer guard based on a null result.
