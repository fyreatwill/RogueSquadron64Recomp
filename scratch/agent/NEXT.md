# NEXT work unit — phase-independent source transition join

HYPOTHESIS-ID: m5-image-task-source-initializer

Session 3571 selected `H-PreTaskZeroContract` only at the target handoff:
target source DMAs and observed source-span writers were zero, but all current
writer hooks are phase-gated. The next bounded change is one regeneration-safe
instrumentation pass that records source-span writes before the target VI phase
and joins the last such transition to the first target source-DMA ordinal.

Competing hypotheses and discriminator:

- H-PreTaskCpuInit: a CPU store or memset changes either source span to
  nonzero before the first target source DMA.
- H-PreTaskOtherInit: a non-CPU operation changes the span, or a host/RSP/DMA
  handoff supplies nonzero data before that DMA.
- H-PreTaskZeroContract: no nonzero transition occurs; the source span is
  already zero when the image-task route begins.

The single discriminating table must include every source-span CPU store,
memset, and DMA write from process start through the first target source DMA,
with phase, guest PC/operation, value or payload hash/nonzero count, and target
route ordinal. A nonzero CPU transition selects `H-PreTaskCpuInit`; a non-CPU
transition selects `H-PreTaskOtherInit`; a live positive-control run with no
nonzero transition selects `H-PreTaskZeroContract` and moves the boundary to
the missing producer/contract before the first observed write.

Before building, verify the oracle core path again; if present, run its
whole-RDRAM positive control and the source-span watch in the same preflight.
Build once with the transition hook, then run from `build/`:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_ALL=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 ./RogueSquadron64Recomp

Require title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, positive
writer/RSP controls, and a non-empty transition table. Stop with SIGKILL and
retain the full log under `scratch/agent/`; do not rewrite source, output, or
PCM state.
