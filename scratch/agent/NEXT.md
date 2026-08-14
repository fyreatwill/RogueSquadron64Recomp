# NEXT work unit (s1153)

HYPOTHESIS-ID: vi-submitgfx-owner

Repeat the live `submitGfxFrame` callsite table with the known phase-relative
input schedule so the port reaches VI-1024. Keep the durable callsite probe
unchanged. The phase-6 `0x800A64AC` row is consistent with the known
`cinematicLoopBody` family, but it is not an owner conclusion until the target
phase is reached.

Competing hypotheses and discriminator:

- H1/mission-owner: mission-family callsite tags fire in the VI-1024 target
  phase.
- H2/cinematic-owner: cinematic/menu callsite tags fire in the target phase
  while mission-family tags remain absent.
- H3/host-only: selector, E9, and slot controls are positive but no generated
  callsite tag fires in the target phase.

The discriminating measurement is one run with all callsite tags, the
`ROGUESQ_LOG_VI_SELECTOR` positive control, `ROGUESQ_LOG_E9_PROVENANCE=1`,
`ROGUESQ_LOG_E9_UNIFIED=1`, slot-dispatch logging, and the 1024 VI phase gate.
A caller-family result is valid only when VI-1024 and at least one E9 row are
observed. A pre-1024 stall or crash is unevaluable.

Build is already complete. Run from the repo root:

    env ROGUESQ_LOG_SUBMIT_GFX_CALLSITES=1 ROGUESQ_LOG_VI_SELECTOR=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_UNIFIED=1 ROGUESQ_LOG_SLOT_DISPATCH=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_PHASE_KEYS_FROM_PHASE=1 PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:start 250:start" PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/soak_results/s1153_vi_submitgfx_callsites 300 2

The s1152 invalid capture is preserved at
`scratch/agent/soak_results/s1152_vi_submitgfx_callsites/`; the corrected
retry is at `scratch/agent/soak_results/s1152_vi_submitgfx_callsites_retry/`.
