# Session 3230 — port route phase join

The Debug target was built once, then silent and image arms were launched
concurrently with LLE-only, spin-yield, `ROGUESQ_LOG_ALL=1`, the validated
autopilot route, VI-caller tracing, receive tracing, and M5 route-state
tracing. Both arms ran for the bounded 60-second capture and were terminated
by the harness with SIGKILL cleanup.

Both arms emitted the same four phase markers and stopped at 640 width with
origin `0x0066A500`; neither reached title 1024, and neither emitted a crash or
abort marker. The independent port evidence was consistent: the 640 VI commit
was `caller=0x80007904`, `requested_width=640`, `committed_origin=0x66A500`,
and the route-state `audio-return` row was in phase 4 at that same origin with
`target=0`. Route-order rows continued after the boundary in both arms.

Retail ground truth from Session 3229 has the caller, reapply entry, reapply
call, and return branch in one ordered 640 transition at origin `0x00790A00`,
then title 1024. Therefore the port and retail observations are not the same
display-mode edge. This selects `H-PhaseDifferentEdge` over `H-PhaseAlias` and
does not select `H-PortSequenceMissing`: the port has a live local return
sequence, but at a different transition.

The whole-run phase markers and identical silent/image route rows are positive
controls for the port capture; the independent retail whole-RDRAM watch and
title gate were already positive controls for the retail execution watches.
No guest value, guard, ordering change, or mitigation was made.
