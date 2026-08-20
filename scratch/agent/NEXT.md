# NEXT work unit (s2003) — attribute the retail audio resident and output ABI

HYPOTHESIS-ID: m5-retail-audio-resident-attribution

## Single work unit

Run the retail oracle positive control first, then make one batched host probe
that scopes every `dma_dmem_to_rdram` write made while an `M_AUDTASK` is
executing. For sampled audio rows, record the complete task descriptor, the
selected function/source identity, DMEM pre/post hashes, every DMEM-to-RDRAM
destination range, direct exit, slot transition, and PCM result. Keep the
current `musyx_stub`/`factor5_ucode_b` A/B only; do not enable `aspMain`, add
another image, reverse a guest gate, or change a guard. Export the runtime
patch, build once, and run both arms concurrently on the same phase schedule.

## Competing hypotheses and discriminating measurement

- **H-image-mismatch:** `factor5_ucode_b` is graphics code being applied to an
  audio task. Its DMEM-to-RDRAM writes will have graphics-like source/dest
  ranges (including the task `data_ptr`/RDP stream), with no audio output range
  and no PCM/slot completion.
- **H-task-staging:** the selected image could be audio, but the port stages a
  wrong DMEM input or task contract. Its observed input/source ranges will not
  match the retail-shaped task data, and the treatment will lack a valid output
  write even though the image's execution footprint is otherwise coherent.
- **H-bridge:** the treatment will write a task-local audio output range or
  produce a nonzero DMEM output, but `queue_samples` will remain all-zero;
  this selects the downstream guest/host bridge.
- **H-gate-scheduler:** the treatment will produce an output range and direct
  completion matching the control, but slot/PCM consumers will not transition
  in the same VI phase; this selects guest gating/scheduling after the RSP.

The discriminator is one phase-gated table of sampled audio rows plus the
same-run `[audtask-dispatch]`, independent `[pcm-sanity]`, slot-writer, and
retail oracle controls. A graphics-like DMA footprint with no audio output
selects H-image-mismatch; an output write plus silent PCM selects H-bridge;
an output write plus absent consumer selects H-gate-scheduler; a missing or
mis-staged input/output contract with no valid write keeps H-task-staging open.
No conclusion is allowed from a null without the whole-RDRAM oracle control.

## Ground-truth command before editing/building

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --watch-write 0x0:0x800000 --watch-write 0x14974C:0x149750 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start > scratch/s73_post_a_scene/m5-audio-step4-oracle.log 2>&1
```

The whole-RDRAM watch must fire and the aligned `0x14974C` watch must fire
from retail PCs. If either control is absent, do not interpret port nulls.

## Exact probe/build/run sequence

1. Add the audio-task scope and DMA-write census in one change to
   `lib/N64ModernRuntime/librecomp/src/rsp.cpp`/`rsp.hpp`. The log must be
   phase-scoped and rate-limited like the existing ABI rows, and must include
   the task's `ucode`, `ucode_data`, sizes, `data_ptr`, `data_size`,
   `dram_stack`, `dram_stack_size`, all DMEM-to-RDRAM `(dmem,len,dram)` ranges,
   and whether each destination overlaps a task-declared output field.
2. Run `./submodule-patches/export.sh` and build:

   ```sh
   cmake --build build --config Debug --target RogueSquadron64Recomp
   ```

3. Run both arms from that one binary:

   ```sh
   env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step4-control 30 12
   env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step4-treatment 30 12
   ```

Use VI 1024/origin `0x00790400` and VI 512/origin `0x006AB400` as the only
phase gates. Do not compare rows by elapsed seconds. Capture both arms even
if one process dies after its phase rows; SIGKILL only at the driver cap.
