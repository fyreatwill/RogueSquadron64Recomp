# NEXT work unit (s2096)

HYPOTHESIS-ID: m5-audio-sp-queue-consumer-boundary

## Work unit

Retain the audio-return wrapper and the post-return route table. After the
retail positive-control run, add one bounded, source-preserving SP-message
table in the runtime. Capture the audio route ordinal when
`sp_complete()` enqueues its external message, carry that source and ordinal
through `enqueue_external_message_src` and `dequeue_external_messages`, and
log the matching guest `osRecvMesg` result for the delivered SP message. Each
row must include edge, arm/ordinal when available, phase/VI, queue/message,
send result, and requeue/full state. Keep the current target-VI gates and the
existing return/route table. No queue policy, gate, wait, guard, output, or
default dispatch change is authorized.

## Competing hypotheses and discriminator

- **H-SPEnqueueMissing** — treatment return/route rows exist, but the
  source-preserving `sp-external-enqueue` row is absent for the same audio
  ordinal. The boundary is before external-queue insertion.
- **H-SPDeliveryNotReached** — treatment enqueue rows exist, but no matching
  delivery row appears, or delivery is `sent=0` with a full/requeued queue.
  The boundary is external-queue draining or queue capacity/scheduling.
- **H-SPGuestConsumerMissing** — treatment delivery rows are `sent=1`, but no
  matching guest `osRecvMesg` row consumes the SP message. The boundary is the
  guest SP consumer.
- **H-RouteRecovered** — treatment retains the complete ordered queue table
  and reaches title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`; the
  existing ABI/DMA/slot/PCM table becomes admissible again.

The discriminator is one same-run ordered table keyed by audio route ordinal:
return → `run-task-return` → `sp-complete-enter` → `sp-complete-return` →
SP external enqueue → external delivery → guest SP receive, with the control
showing the same positive sequence. A treatment row missing at the first edge
selects `H-SPEnqueueMissing`; enqueue without successful delivery selects
`H-SPDeliveryNotReached`; successful delivery without guest receive selects
`H-SPGuestConsumerMissing`; both target VIs select `H-RouteRecovered`. If the
control lacks the ordered queue sequence, classify the instrument as invalid
and do not interpret the treatment.

## Exact commands

Run the independent ground-truth recipe before editing or building:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x14998A:0x14998C --watch-write 0x14974C:0x149750 --first-watch 0 --detail-watch 1 --pc-hist-watch 1 --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-pc 0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ED48 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Edit the source-preserving route table in
`lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp` and its runtime hook
declarations as needed. Then export, build once, and run both arms together:

```sh
./submodule-patches/export.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step5-treatment 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step5-treatment-driver.log 2>&1 &
pid_t=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step5-control 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step5-control-driver.log 2>&1 &
pid_c=$!
wait $pid_t; rc_t=$?
wait $pid_c; rc_c=$?
printf 'treatment_rc=%s control_rc=%s\n' "$rc_t" "$rc_c"
```

Inspect only bounded counts, target phase lines, crash markers, and the
ordered queue rows from both `run.log` files. If either arm misses its target
VIs, classify only the queue/consumer boundary; do not interpret pre-target
ABI, DMA, slot, or PCM fields.
