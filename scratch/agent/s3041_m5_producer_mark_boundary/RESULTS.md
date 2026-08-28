# Session 3041 M5 producer-mark route boundary

The independent retail oracle passed the whole-RDRAM positive control at
10,000 writes, reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and recorded 2,470 executions of
`bufferArbiterProducerMark` at `0x8001BCE4`. Its predecessor distribution was
`0x8000C628: 2446`, `0x8000BFE8: 7`, `0x8001A300: 6`, `0x8000C440: 6`, and
`0x80018258: 5`.

The same-build port capture used the AUTOPILOT route and full route marker
set. It reached only VI 640 at `0x0066A500` and never reached title or hangar.
The positive controls fired before the boundary: 526 route-prepare rows, 70
route-transition rows, 5 route-state rows, 4 B40 rows, and 27 real Factor 5
audio-task dispatch rows. At VI 640, route preparation remained
`accepted=0`; there were no producer-mark candidate rows. The run had no crash
or abort marker and the 512 phase gate timed out after 90 seconds.

Verdict: `RouteFailure` for this capture. Retail ProducerMark execution is
confirmed independently, but the port-side producer-mark/caller comparison is
unevaluable because the port has no target phase. No audio hypothesis was
selected and no behavior or mitigation changed.

Evidence: `run.log`; the retail oracle output is recorded in the session 3041
ledger entry.
