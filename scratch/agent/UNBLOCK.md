# Unblock result — 2026-08-28

Route taken: 3, re-scope.

Route 1 did not refute the dependency. The current Debug binary was run with
the documented LLE-only, spin-yield, autopilot, and phase-gated probe settings.
The same run observed eight host input controls and VI 640 at
`0x0066A500`, then timed out waiting for VI 1024 after 60 seconds.

Route 2 did not satisfy it locally. Source inspection shows
`ROGUESQ_M4_Y8000_WIDTH` only selects an M4 probe width; it is not a route
control. Existing dirty submodule patches contain no selected upstream route
change, and no behavior-changing route modification was inferred.

The M5 route dependency is therefore open, but the project is not stopped.
`scratch/agent/NEXT.md` now selects a bounded M3 NULL-plus-offset idiom-class
audit that does not require target-phase audio controls. No runtime behavior
was changed.

Evidence: `scratch/agent/unblock_route_probe_20260828/`.
