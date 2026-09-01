# M5 session 3554 — canonical heap route crashed before target phases

The prescribed real-audio/LLE-solo/spin-yield/autopilot capture used the
existing regeneration-safe heap caller table and no state-changing
instrumentation. The autopilot arm was reported armed, and the capture
reached VI 640 (`0x0066A500`), but it never reached VI 1024 or VI 512.

The heap table was active before the crash: 32 caller rows came from edge
`0x800104A8`, 32 from edge `0x80010CD8`, and 32 matching callee-entry rows.
Because all rows were pre-title phase 3, they cannot be joined to target-phase
behavior. The process then emitted a crash marker for SIGBUS at
`slotDispatcherIter+3508`, with guest PC `0x80007904` and fault address
`0x37fff0019`.

This selects `H-RouteCrashes` over `H-RouteRequalifies`. It does not select
either heap caller for the target route, and it does not classify the cached
head or its writer. The next boundary is the pre-title audio-slot dispatcher
route that prevents the qualified capture from reaching the target phases.

ORIGIN: no mitigation or game-state write was added; this is diagnostic-only
route evidence.

Evidence: `scratch/agent/s3554_m5_heap_route_requalify/run.log`.
