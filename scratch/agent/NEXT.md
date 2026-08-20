# NEXT work unit (s2069)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Add a diagnostic-only, environment-gated within-run A/B for the host's DMEM
canary prefill at `0xF80..0xF8F`. With `ROGUESQ_AUDIO_CANARY_AB=1`, alternate
canary-on and canary-off image tasks by phase-keyed task ordinal; leave the
default canary-on behavior unchanged. Log the arm beside the existing
`audtask-abi`/DMA rows and retain the exact E50 DMA payload fields. Because this
touches `lib/N64ModernRuntime`, export the submodule patch in the same change.
Run both arms in one qualified route; do not change task fields, dispatch,
guest values, output routing, waits, or guards.

## Competing hypotheses and discriminator

- **H-CanaryObserver** — the prefill is overwritten before any relevant read;
  canary-on and canary-off rows have the same `exit`, DMEM changes, exact-E50
  payload, and PCM joins.
- **H-CanaryPoison** — the canary bytes are consumed before the generated
  output loops overwrite them; canary-off image rows improve the `Broke`,
  canary, exact-E50 payload, or nonzero-PCM contract while input spans remain
  matched.
- **H-CanaryContract** — the bytes are part of a required task-side DMEM
  contract; canary-off changes the task but does not produce a valid output,
  selecting the reserved-gap/ABI boundary rather than a harmless observer.

The discriminator is one phase-keyed table for both arms: arm, `data_ptr` and
`data_size`, source-span FNV/nonzero count, DMEM pre/post/change range, exit,
canary result, every exact E50 DMA span's FNV/nonzero count, and paired PCM
source/consumer rows. Positive controls are both target VI anchors, live input,
and the existing stub/image dispatch controls; no conclusion may use a canary
counter alone. H-CanaryPoison requires a canary-off improvement with matched
source spans; H-CanaryContract requires a canary-off change without a valid
output; unchanged rows select H-CanaryObserver.

## Exact commands

1. Patch `lib/N64ModernRuntime/librecomp/src/rsp.cpp` so the existing canary
   fill is skipped only when `ROGUESQ_AUDIO_CANARY_AB=1` and the phase-keyed
   image-task ordinal is odd; log `canary_arm=on|off` in the ABI and DMA rows.
   Hash the task's `data_ptr..data_ptr+data_size` source span before the ucode
   call and include its FNV/nonzero count in the same row. No default behavior
   change. Add an `ORIGIN:` line naming the host canary writer and the
   generated `factor5_ucode_b` DMEM output loops; state that legitimacy is the
   question under test.
2. Export and build the one modified submodule:

   ```sh
   ./submodule-patches/export.sh
   cmake --build build --config Debug --target RogueSquadron64Recomp
   ```

3. Run the qualified route once with both arms enabled in-process:

   ```sh
   env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUDIO_CANARY_AB=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-canary-ab 30 12
   ```

4. Verify title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, the paired
   arm/source/E50/PCM table, no crash or abort marker, and `git diff --check`.
   Kill any wrapper-owned game process with SIGKILL after the capture window.

The exact E50 retail ownership from s2068 is the ground-truth reason this
instrument is scoped to the DMEM canary/output contract; do not reinterpret a
canary-off result as permission to remove the reservation until the table
selects it.
