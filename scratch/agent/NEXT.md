# NEXT work unit (s2095)

HYPOTHESIS-ID: m5-audio-postreturn-route-state

## Work unit

Retain the s2094 audio-return wrappers. First rerun the fixed retail oracle
positive-control recipe below. Then add one bounded, regeneration-independent
route table to the runtime around the audio task's `run_task` return and the
task-thread SP completion path: log `run-task-return`, `sp-complete-enter`, and
`sp-complete-return` for `M_AUDTASK`, with arm, phase/VI, ordinal, exit/result,
and a per-phase row. The post-return rows must be emitted only after the
existing audio-return wrapper has returned. Export the submodule patch after
editing under `lib/`, build once, and run the default stub control and
`ROGUESQ_AUDIO_UCODE=1` treatment concurrently from the same driver. Keep all
guest gates, waits, guards, host output routing, default dispatch, and target
phase filters unchanged.

## Competing hypotheses and discriminator

- **H-TaskThreadBoundary** — treatment audio-return rows are present, but a
  matching `run-task-return` or `sp-complete-enter` row is missing. The task
  thread is the immediate post-return boundary.
- **H-SPRouteQueued** — each observed treatment return has a matching successful
  `run-task-return`, `sp-complete-enter`, and `sp-complete-return` row, but the
  treatment still misses both target VIs. The host task completion/enqueue path
  is crossed; the next boundary is SP queue delivery or the guest consumer.
- **H-RouteRecovered** — the treatment retains the complete route sequence and
  reaches both target VIs. The existing ABI/canary/slot/PCM table becomes
  admissible again.
- **H-ControlProbeFailure** — the control does not show the same ordered route
  sequence after its known `musyx_stub` returns. The instrument is invalid and
  the A/B is unevaluable.

The discriminator is the same-run ordered table keyed by audio-return ordinal:
return → `run-task-return` → `sp-complete-enter` → `sp-complete-return`, plus
the title/hangar VI gates. A control row sequence is the positive control; do
not infer from a route counter alone. A complete treatment sequence with no
target VI selects `H-SPRouteQueued`; a missing treatment post-return edge
selects `H-TaskThreadBoundary`; target VIs select `H-RouteRecovered`.

## Exact commands

Run the independent ground-truth recipe before editing or building:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x14998A:0x14998C --watch-write 0x14974C:0x149750 --first-watch 0 --detail-watch 1 --pc-hist-watch 1 --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-pc 0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ED48 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Edit the two runtime route sites, then export the submodule patch and build:

```sh
./submodule-patches/export.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run both arms concurrently:

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step4-treatment 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step4-treatment-driver.log 2>&1 &
pid_t=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step4-control 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step4-control-driver.log 2>&1 &
pid_c=$!
wait $pid_t; rc_t=$?
wait $pid_c; rc_c=$?
printf 'treatment_rc=%s control_rc=%s\n' "$rc_t" "$rc_c"
```

Inspect only bounded counts and ordered rows from both `run.log` files. If
either arm misses its target VIs, classify only the return/route boundary; do
not interpret pre-target ABI, DMA, slot, or PCM fields.
