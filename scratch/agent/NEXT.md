# NEXT work unit — bounded M5 host-completion/route-order audit

HYPOTHESIS-ID: m5-route-host-completion-order

Join the port's host-side `send_dl` return, `dp_complete`, external-message
delivery, and subsequent live-VI route-preparation attempt. Session 3051
proved the retail guest receive/forward pair, but the port stopped at VI 640,
so the next discriminator must explain ordering before target-phase entry.

Competing hypotheses and the discriminator:

- H-CompletionNotObserved: `send_dl` returns without the corresponding
  `dp_complete`/external delivery before route preparation.
- H-CompletionOrderingDivergent: all edges occur, but delivery or queue drain
  is ordered after the route attempt that remains at VI 640.
- H-CompletionEquivalent: all host edges occur in the expected order and the
  VI-640 boundary is elsewhere.
- H-MeasurementInsufficient: route or edge controls do not arm in the same
  capture.

The single discriminator is one phase-keyed port table containing task
ordinal, `send_dl` return, `dp_complete`, external enqueue/delivery source,
queue state, and the immediately following route-preparation result. Missing
completion selects NotObserved; a changed edge order selects
OrderingDivergent; matching edges with a failed route select Equivalent; an
unarmed route control selects Insufficient.

Commands:

1. Audit existing host edge call sites:
   `rg -n -C 18 'send_dl\\(|dp_complete\\(|enqueue_external_message_src|route_prepare|accepted=' src lib`
2. Add one batched phase-keyed port table at those existing edges, then build:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run from `build/` with LLE-only AUTOPILOT, `ROGUESQ_LOG_PHASE=1`, and the
   route positive controls; capture to a non-dot final path and SIGKILL it.

Expected outcomes: each hypothesis must receive a named observable outcome;
no behavior change is justified by another route-null or by event wiring alone.
