# Next work unit

HYPOTHESIS-ID: m5-step1-qualification

Closed M3 classes: mem access, divide, float->int, float compare, FCSR, mult/dmult, trap/break/syscall/cop0, unaligned/ll-sc/cache (s4820), indirect jr/jalr (s4821).

Next iteration's single work unit is a fresh M5 Step 1 same-build phase-gated A/B
qualification, using the existing image arm and silent control. Competing
hypotheses and discriminator:

* H-AudioDegeneracy: the silent path suppresses downstream service/slot/PCM
  work. Select if the image arm reaches the target phase and adds service,
  slot, voice, or PCM joins while the stub remains a valid no-DMA control.
* H-ContractGap: the image runs but its task/DMEM/DMA/SP contract is
  incomplete. Select if image DMEM/DMA and completion fire but downstream
  task-field/service/slot/PCM joins do not close.
* H-RequestOnlyLifecycle: one-shot SP request-only handling changes route
  progress. Select only if request-only loses the target phase or scheduler
  return while completion-wins reaches it in the same run pair.

The discriminating measurement is the harness gate at VI 640 plus the paired
rows for image/stub dispatch, task exit, SP completion, viewer return, E60/E70/
E80F, title VI 1024, and hangar VI 512. The whole-RDRAM oracle control is
already required by the plan; no new instrument is added.

Exact command: `zsh tools/run_m5_yield_ab.sh` from the repository root. Expected
outcomes: `H-RequestOnlyOneShotNotCausal` rejects the lifecycle hypothesis;
`H-RequestOnlyLifecycleCausal` selects it; `H-CoverageInvalid` or
`H-DiscriminatorIncomplete` means the target phase/control was absent and no
audio conclusion is allowed.

This iteration's two attempts were route-invalid: the bare harness reached VI
640 but not title/hangar, and the qualified tuple
`ROGUESQ_AUTOPILOT=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1
ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1` stopped at VI
320/default or crashed request-only at `spTaskSchedulerThread+9632`. Before
rerunning, verify the binary/ROM and capture the startup crash context; do not
interpret either attempt as an audio result.
