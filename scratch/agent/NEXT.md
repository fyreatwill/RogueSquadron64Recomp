# NEXT work unit (s2070)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Rerun the existing diagnostic-only canary A/B on the fully qualified M5 route.
The s2069 instrument is already built and exported; do not change its logic or
guest behavior. With `ROGUESQ_AUDIO_CANARY_AB=1`, alternate canary-on and
canary-off image tasks by phase-keyed task ordinal, and collect the complete
source/E50/PCM table with `ROGUESQ_M5_C88_VALUE=1` and
`ROGUESQ_SPIN_YIELD=1`. Do not change task fields, dispatch, guest values,
output routing, waits, or guards.

ORIGIN: the host writes the `0xF80..0xF8F` canary; generated
`factor5_ucode_b` loops at `L_146C`, `L_1D24`, and `L_1F40` are the guest-side
writers under test. The legitimacy of the reserved-gap assumption is not
established by ownership alone.

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

1. Ask ground truth first with the corrected Rice oracle. Require the
   whole-RDRAM positive-control threshold, title VI `1024 @ 0x00790400`,
   hangar VI `512 @ 0x006AB400`, and nonzero exact-E50 writes.
2. Build the already committed diagnostic:

   ```sh
   ./submodule-patches/export.sh
   cmake --build build --config Debug --target RogueSquadron64Recomp
   ```

3. Run both arms once in-process on the complete tuple. The wrapper supplies
   `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`:

   ```sh
   env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUDIO_CANARY_AB=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-canary-ab-c88 30 12
   ```

4. Verify title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, the paired
   arm/source/E50/PCM table, and the live input/image dispatch controls. A
   no-crash capture is required for hypothesis selection; if the known odd-ROM
   DMA assertion recurs, record the table as inadmissible and do not infer from
   the canary fields alone. Run `git diff --check`.
   Kill any wrapper-owned game process with SIGKILL after the capture window.

The exact E50 retail ownership from s2068 is the ground-truth reason this
instrument is scoped to the DMEM canary/output contract; do not reinterpret a
canary-off result as permission to remove the reservation until the table
selects it.
