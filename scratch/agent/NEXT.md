# NEXT work unit — bounded M5 gfx action-order audit

HYPOTHESIS-ID: m5-route-gfx-action-order

Audit the single gfx-thread action path around `sp_complete`, `send_dl`,
`dp_complete`, and display-list callbacks. Session 3052 showed that host DP
completion and delivery occur in order, but the port still stops at VI 640.

Competing hypotheses and the discriminator:

- H-GfxActionOrderingWrong: the gfx action path orders SP/DP completion or
  callbacks differently from the expected handoff and stalls the route.
- H-GfxActionOrderingEquivalent: the action path order is internally
  consistent, so the VI-640 boundary is elsewhere.
- H-DeliveryAfterRoute: DP delivery is observed only after a route attempt
  that has already failed.
- H-MeasurementInsufficient: the phase or action controls do not arm.

The single discriminator is one phase-keyed port table containing action
dequeue ordinal, pre-send `sp_complete`, `send_dl` return, `dp_complete`, DP
external enqueue/delivery, display-list callback order, and the immediately
following route-preparation result. A changed action order selects
GfxActionOrderingWrong; delivery after route failure selects
DeliveryAfterRoute; matching order with failed route selects
GfxActionOrderingEquivalent; an unarmed control selects Insufficient.

Commands:

1. Audit the gfx action path:
   `rg -n -C 30 'SpTaskAction|sp_complete\\(|send_dl\\(|dp_complete\\(|on_displaylist_|route_prepare|accepted=' lib/N64ModernRuntime/ultramodern/src/events.cpp src/main/rt64_render_context.cpp src/main/upstream_compat.cpp`
2. Add one batched phase-keyed table at those existing edges, then export and build:
   `./submodule-patches/export.sh && cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run from `build/` with LLE-only AUTOPILOT, `ROGUESQ_LOG_PHASE=1`, and route
   positive controls; capture to a non-dot final path and SIGKILL it.
