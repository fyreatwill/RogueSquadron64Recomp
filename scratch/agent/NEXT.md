# NEXT work unit (s2097)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Use the now-qualified SP route as the positive control and interpret the
existing phase-keyed image-task contract table in one same-build concurrent
A/B: `audtask-abi`, `audtask-dma-row` plus every `audtask-dma-range`,
`audtask-join`/`audtask-join-range`, PCM source/consumer, and the existing
phase-keyed slot/gate rows. Do not change task fields, output routing, canary,
gate, wait, guard, queue policy, or default dispatch. The route table must
retain its partial-order rule: enqueue precedes delivery and guest receive,
enqueue precedes `sp-complete-return`, and delivery precedes guest receive;
delivery may race `sp-complete-return`.

## Competing hypotheses and discriminator

- **H-ImageOutputContract** — target-phase treatment rows include a
  `dmem_to_rdram` range with `output_overlap=1` and `payload_nz>0`, and the
  same audio ordinals have admissible PCM source/consumer joins. The generated
  image task is writing the host output contract.
- **H-ImageStagingZeroPayload** — target-phase treatment rows show
  `dmem_changed>0` and route completion, but every image DMA range has
  `output_overlap=0` or `payload_nz=0`, with `output_buff=0` and no admissible
  output/PCM join. The boundary is image staging, destination selection, or
  task ABI interpretation.
- **H-GuestCompletionContract** — image DMA/PCM evidence is present, but the
  phase-keyed slot/gate rows diverge from the control or `audtask-join` has a
  systematic `complete=0`/post-task consumer split. The remaining contract is
  guest completion/slot reaping rather than SP queue delivery.
- **H-ContractQualified** — target-phase treatment retains output/PCM and
  slot/gate joins with the control, so the image arm's ABI/DMA/slot/PCM fields
  are qualified for the next incremental audio change.

The discriminator is one table keyed by arm, phase/VI, and audio task ordinal:
`audtask-abi` exit/canary/DMEM fields → all DMA direction/range overlap and
payload fields → `audtask-join` source/consumer/complete fields → PCM
source/consumer hash/count fields → slot/gate rows. The control must retain
complete route ordinals and the retail oracle must pass its whole-RDRAM
positive control. Treatment output-overlap plus nonzero payload and matched
PCM selects `H-ImageOutputContract`; route-complete zero-payload/non-overlap
selects `H-ImageStagingZeroPayload`; a systematic slot/gate or completion split
selects `H-GuestCompletionContract`; matched contract rows select
`H-ContractQualified`. No conclusion is allowed from pre-target rows if an arm
misses both target VIs.

## Exact commands

Run the independent ground-truth recipe before interpreting the port table:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x14998A:0x14998C --watch-write 0x14974C:0x149750 --first-watch 0 --detail-watch 1 --pc-hist-watch 1 --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-pc 0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ED48 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Build once, then run both arms concurrently from the same driver:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step6-treatment 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step6-treatment-driver.log 2>&1 &
pid_t=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step6-control 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step6-control-driver.log 2>&1 &
pid_c=$!
wait $pid_t; rc_t=$?
wait $pid_c; rc_c=$?
printf 'treatment_rc=%s control_rc=%s\n' "$rc_t" "$rc_c"
```

Inspect only bounded counts and phase-gated rows from the two `run.log` files:
target phases/crash markers, complete route ordinals, `audtask-abi`,
`audtask-dma-range`, `audtask-join`, PCM source/consumer pairs, and slot/gate
rows. Use `awk` to classify all target-phase treatment DMA ranges and joins in
one pass; do not infer from a single sampled row.
