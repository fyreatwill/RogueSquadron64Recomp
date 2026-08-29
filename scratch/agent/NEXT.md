# NEXT work unit — M5 target-phase qualification after route selection

HYPOTHESIS-ID: m5-target-phase-route-boundary

## Single work unit

M5 target-phase qualification remains blocked: do not repeat the `s2618` or
eleven-Start routes. A12 is closed (s3221/s3222: the only guest stores of
`0x8014974C` are named binary-gate publications, selects H-NamedFlagWriter).
The next unit can run only after a human-selected route change or an equivalent
retail-grounded boundary is available.

The recv-trace instrumentation (`ROGUESQ_RECV_TRACE`) in upstream_compat.cpp
is passive and env-gated; it is available but was not run in s3221.

## Competing hypotheses for the next qualification run

- `H-TargetRouteUnblocks`: the selected route reaches title 1024 and hangar
  512, making target-phase audio joins evaluable.
- `H-TargetRouteStillStops`: the selected route still stops before title,
  keeping audio/task/DMA/service/slot/voice/PCM rows unevaluable.
- `H-TargetRouteCrashes`: the route reaches a crash/abort before the target
  phase and supplies a new discriminating failure boundary.

## Discriminator

Phase-gated same-build `ROGUESQ_AUDIO_UCODE=0/1` arms after the route change.
Require the image arm's DMEM, DMA, SP completion/Broke, service, slot, and PCM
joins, with the silent arm as the no-write control. Record VI 640/1024/512
transitions; do not use elapsed time.

## Exact start after route selection

Build the existing Debug target, then run the documented phase-gated pair
concurrently from `build/` with `ROGUESQ_AUDIO_UCODE=0/1` and
`ROGUESQ_LOG_ALL=1`; capture each arm to a non-dot final path and SIGKILL both
processes at the watchdog boundary.
