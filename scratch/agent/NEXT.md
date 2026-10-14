# Next work unit

HYPOTHESIS-ID: m5-step1-qualification

Closed M3 classes: mem access, divide, float->int, float compare, FCSR, mult/dmult, trap/break/syscall/cop0, unaligned/ll-sc/cache (s4820), indirect jr/jalr (s4821).

Next iteration's single work unit is a route qualification for the existing M5
Step 1 same-build phase-gated A/B, using the existing image arm and silent
control. Do not interpret another target-absent A/B. First identify the route
stop after VI 640 from the existing logs/build configuration, then make one
bounded route-validating change or measurement before rerunning the A/B.
Competing
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

Exact command after route qualification: `zsh tools/run_m5_yield_ab.sh` from the
repository root. Expected outcomes: `H-RequestOnlyOneShotNotCausal` rejects the
lifecycle hypothesis; `H-RequestOnlyLifecycleCausal` selects it;
`H-CoverageInvalid` or `H-DiscriminatorIncomplete` means the target phase/control
was absent and no audio conclusion is allowed.

This iteration's same-build pair was route-invalid: both arms passed the VI-640
and SP-completion controls but stopped before title/hangar. Default produced 4
completion-wins rows; request-only produced 7 request-only rows and E70/E80F
rows. No audio result was obtained.
