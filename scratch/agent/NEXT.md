# NEXT work unit — validate the M5 guard on a configured MIPS host

HYPOTHESIS-ID: m5-step3-guard-validation

Run the exact configured `PatchesLib` build on a Windows/MIPS host (or with
equivalent Rogue Squadron generated patch artifacts), then run the existing
bounded M5 Step 3 validation. Do not substitute the sibling Starfox artifact,
Clang, or the host-only N64Recomp binary. Do not change audio behavior unless
the Step 3 target-phase row identifies one writer/consumer relation.

## Competing hypotheses

- `H-GuardValidated`: the configured patch build succeeds and the guard can be
  validated in the existing Step 3 recipe.
- `H-GuardHostMissing`: the configured/generated prerequisite is unavailable,
  so no guard or M5 behavior conclusion is possible.
- `H-Step3EdgeSelected`: the build succeeds and target-phase controls identify
  one legitimate missing edge for a later bounded behavior change.

## Discriminator

The build result is the first discriminator: success permits the existing
Step 3 recipe; missing target/toolchain/generated output selects
`H-GuardHostMissing`. If Step 3 runs, require whole-RDRAM/VI controls plus the
target framebuffer physical address, VI origin, caller/order, image-vs-silent
distinction, task/DMA/SP completion, service, slot, and PCM joins. Only a
like-for-like mismatch or a newly proven legitimate writer/consumer edge
selects `H-Step3EdgeSelected`; otherwise leave behavior unchanged.

## Exact commands

1. On the configured host: `cmake --build build --config Debug --target PatchesLib`.
2. If it succeeds, run the existing bounded Step 3 recipe with both
   `ROGUESQ_AUDIO_UCODE=0` and `ROGUESQ_AUDIO_UCODE=1` in one build/run plan,
   phase-gated by `PROBE_PHASE_WIDTH` and `PROBE_KEYS_FROM_PHASE=1`.
3. Record the build and validation result in `scratch/agent/`, then update the
   ledger. No mitigation is authorized from a failed prerequisite.

The completed status-03 audit is evidence only; it does not waive this M5
prerequisite.
