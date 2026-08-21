# NEXT work unit (s2137) — same-build port task ABI comparison

HYPOTHESIS-ID: m5-port-task-contract

## Work unit

Run one same-build, two-arm port comparison of the existing `musyx_stub`
control and opt-in `factor5_ucode_b` image arm. Use the phase-keyed existing
`[audtask-abi]`, `[audtask-dma-range]`, `[pcm-boundary-source]`,
`[pcm-boundary-consumer]`, and `[audio-return]` witnesses. Both arms must be
launched in this iteration and both must pass the positive LLE/audio controls
and reach title VI `1024 @ 0x00790400` plus hangar VI `512 @ 0x006AB400`.
No task-field rewrite, output-route change, new RSP config, or default-arm
change is in scope.

## Competing hypotheses and discriminator

- `H-PortTaskFieldsMatchRetail`: both arms receive the same task fields as the
  retail table (`ucode=0x80099FE0`, `ucode_data=0x800A4E00`, nonzero
  `data_ptr`/`data_size`, zero output buffer); the image's observed DMA range
  at `data_ptr+0x100` and its phase-keyed PCM source/consumer join are the
  meaningful output boundary.
- `H-PortOutputBuffMismatch`: the image arm writes or consumes a nonzero
  `output_buff` range, or its DMA rows overlap that field, unlike retail's
  zero-write output-buffer contract.
- `H-PortDataPtrMismatch`: the image arm has the retail task fields but its
  source hash, DMA destination, or PCM join does not preserve the
  `data_ptr+0x100` relationship.
- `H-PortTaskComparisonUnresolved`: either arm misses a target phase or a
  positive control, or the phase-keyed rows are absent/conflicting.

The one discriminating table is keyed by arm, target phase, and audio row:
all task fields, source hash/nonzero count, every dmem-to-RDRAM destination
and overlap flag, image exit/break PC, and source/consumer PCM address,
length, hash, and nonzero count. Select the first hypothesis only if both
arms have target controls and the image rows preserve the retail field
contract plus `data_ptr+0x100` output relation. Select the output-buffer or
data-pointer hypothesis only from a same-build image-vs-stub split with the
corresponding row. Otherwise select the coverage/unresolved hypothesis and
make no runtime change.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp
    mkdir -p scratch/agent/s2137_stub scratch/agent/s2137_image
    set +e
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_SP_TASKS=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS="3:start 7:start 11:start" zsh tools/probe.sh scratch/agent/s2137_stub 45 1 > scratch/agent/s2137_stub_driver.log 2>&1 & p_stub=$!
    env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_SP_TASKS=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS="3:start 7:start 11:start" zsh tools/probe.sh scratch/agent/s2137_image 45 1 > scratch/agent/s2137_image_driver.log 2>&1 & p_image=$!
    wait $p_stub; rc_stub=$?; wait $p_image; rc_image=$?; echo "stub=$rc_stub image=$rc_image"

Inspect only the bounded target-phase rows, plus the positive-control counts
and phase transitions:

    grep -hE '\[audtask-abi\]|\[audtask-dma-range\]|\[audio-return\]|\[pcm-boundary-(source|consumer)\]|\[audtask-dispatch\]|\[phase\]' scratch/agent/s2137_stub/run.log scratch/agent/s2137_image/run.log | tail -400

Do not interpret missing rows from an arm that failed to reach both target
phases as a null result.
