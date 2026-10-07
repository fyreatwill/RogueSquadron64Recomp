# Next work unit: qualify the M5 status-03 worker boundary

HYPOTHESIS-ID: m5-status03-worker-join

Run one qualified silent-arm investigation of the status-03 worker. The
external generated tree must be instrumented as one phase-scoped table joining
`serviceVoicePoolFrame` entry, the guest `0x8009B7EC` zeroing store, and the
worker shutdown return. Do not replace the wait, force-clear status, or add a
guard during this unit.

Competing hypotheses and discriminator:

- H-status03-port-writer: the qualified port executes the named zeroing store
  between worker entry and shutdown return, establishing the port-side writer
  ordering.
- H-status03-port-no-writer: the qualified port reaches the worker boundary
  but no named zeroing store occurs before return, separating the port worker
  from the retail writer witness.
- H-status03-route-invalid: the silent arm misses title/hangar or crashes before
  the joined table is phase-qualified; no writer conclusion is allowed.

The single discriminating measurement is a phase-keyed entry/store/return join
on a route that passes the whole-RDRAM retail positive control plus title 1024
and hangar 512. Entry with a store before return selects the writer-ordering
hypothesis; entry/return without the store selects no-writer; either missing
phase gate or a pre-gate crash selects route-invalid. A counter that merely
proves the branch ran is not sufficient.

Before running, inspect the existing M5 audio plan and generated-tree probe
helpers for the exact source and fixup locations. Then build once with all
entry/store/return counters and run the retail control and silent port arm.
Use `PROBE_PHASE_WIDTH` and `PROBE_KEYS_FROM_PHASE=1`; kill only with SIGKILL.
If the external generated tree or required toolchain is unavailable, record
the measured failure and a falsifiable retry condition rather than changing the
worker behavior.
