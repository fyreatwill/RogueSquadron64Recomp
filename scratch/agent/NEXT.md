# NEXT work unit (s1152)

HYPOTHESIS-ID: vi-submitgfx-owner

Add phase-scoped markers at every generated `submitGfxFrame` callsite, tagged
with the static caller guest address. Do not repeat the shared-entry `$ra`
probe: s1151 showed `ctx->r31 == 0` for all 457 entry rows under the generated
C-call ABI.

Competing hypotheses and discriminator:

- H1/mission-owner: post-640 calls are emitted by callsites in the mission
  frame-loop family; those static caller tags fire after the 640 transition.
- H2/cinematic-owner: post-640 calls are emitted by cinematic/menu callsites;
  those tags fire while mission-family tags remain absent.
- H3/host-only: selector positive control, task-control E9, and slot dispatch
  remain live but no generated callsite tag fires in the target phase.

The discriminating measurement is one build/run containing all callsite tags,
the independent `ROGUESQ_LOG_VI_SELECTOR` positive control, task-control E9,
slot-dispatch logging, and the 1024 VI phase gate. A caller-family result is
valid only when VI-1024 and the E9 positive control are both observed; an
early crash or pre-1024 stall is unevaluable.

Use the durable fixup/regeneration path. The currently available generated
output is already fixup-sentinel-marked, so extend the controlled fixup mode
in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` rather
than editing generated C by hand. Build with:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Run from `build/`, capture under
`scratch/agent/soak_results/s1152_vi_submitgfx_callsites/`, arm the selector,
E9, slot, and passive breadcrumb env vars, and kill with SIGKILL through
`tools/probe.sh`.
