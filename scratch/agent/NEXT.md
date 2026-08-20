# NEXT work unit (s2002) — map the audio task/DMEM ABI boundary

HYPOTHESIS-ID: m5-audio-task-abi-boundary

## Single work unit

Before building an instrument, run the retail oracle with its whole-RDRAM
positive control and the known retail `0x14974C` writer watch. Then extend the
existing `run_task` audio row in one batched change to record the complete
`OSTask` audio descriptor (`ucode`, `ucode_data`, `ucode_data_size`, `data_ptr`,
`data_size`, `dram_stack`, `dram_stack_size`), a pre/post DMEM hash, changed-byte
count and first/last changed offsets, the existing canary result, direct exit,
and the existing slot/PCM outcomes. Keep the dispatch toggle and all guest
gate stores unchanged.

## Competing hypotheses and discriminating measurement

- **H-task-staging:** `factor5_ucode_b` is the intended engine image, but the
  port presents a wrong task descriptor or DMEM input. Treatment descriptors
  or pre-DMEM hashes will differ from the retail-shaped task contract, and its
  changed ranges will not contain a valid audio output region.
- **H-wrong-resident-abi:** the opt-in image is not the retail MusyX/MORT
  resident for these tasks. Descriptor fields look structurally valid, but the
  treatment's changed-range signature is incompatible with the control and
  retail writer/PC evidence, with no valid slot/PCM result.
- **H-bridge:** the RSP task produces an output buffer and treatment DMEM has a
  nonzero output-range signature, but `queue_samples` still reports all-zero
  PCM. This selects the downstream guest/host audio bridge rather than the RSP
  image.
- **H-gate-scheduler:** descriptor and DMEM signatures are valid and match the
  control, but slot/PCM completion is suppressed by the unchanged guest gate or
  scheduler. This requires a treatment-side task/output row without a matching
  consumer transition.

The discriminator is one phase-gated table containing every sampled audio task
row plus the same-run `[audtask-dispatch]` control, independent PCM callback,
and named slot-writer rows. A canary-only difference is insufficient: an output
range plus nonzero PCM selects H-bridge; a descriptor/DMEM mismatch with no
output selects H-task-staging or H-wrong-resident-abi; matching output with no
consumer selects H-gate-scheduler. Missing title/hangar rows without the
whole-RDRAM oracle control are UNEVALUABLE.

## Exact commands

Run this ground-truth control before adding/building the port probe:

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --watch-write 0x0:0x800000 --watch-write 0x14974C:0x149750 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start > scratch/s73_post_a_scene/m5-audio-step3-oracle.log 2>&1
```

After the single probe change, build once and run both arms from that same
binary and phase schedule in separate capture directories. Use SIGKILL only
after the driver reaches its cap:

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step3-control 30 12
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step3-treatment 30 12
```

Use VI 1024/title and `0x006AB400`/512 hangar rows as phase gates. Roll back
the treatment by unsetting `ROGUESQ_AUDIO_UCODE`; do not enable `aspMain`, flip
another `0xF50` store, remove a guard, or default the opt-in arm.
