# NEXT work unit — trace the selected caller mismatch

HYPOTHESIS-ID: m5-port-zero-pcm-source

Do exactly one bounded M5 caller-mismatch census next iteration. Do not modify
output, waits, slots, status handling, consumer dispatch, or PCM writeback.

Competing hypotheses:

- `H-PortCaller8002BEECAbsent`: the port never reaches the retail target
  caller, so `0x8008F2CC` is a different legitimate initialization path.
- `H-PortCallerArgumentConstruction`: both paths are reached, but their
  destination/length/value or task-row construction differs.
- `H-PortCallerDispatchAlias`: the port reaches the retail caller through a
  dispatch/overlay alias that changes the observed callsite.

Discriminating measurement: ask the retail oracle for phase-gated execution and
argument rows at `0x8002BEEC` and `0x8008F2CC`, plus the writer and whole-RDRAM
control. Batch a port census keyed by caller PC, destination, fill/value, len,
phase, and audio-task ordinal/row. Retail caller activity with no matching
port row selects `H-PortCaller8002BEECAbsent`; matching activity with a tuple
difference selects `H-PortCallerArgumentConstruction`; matching tuple under a
distinct dispatch path selects `H-PortCallerDispatchAlias`.

Before building, verify oracle watch indices and existing port caller hooks.
Keep phase, audio-task/ABI, PCM, image-stage/DMA, title, and hangar controls
live. If code under `lib/` changes, run
`./submodule-patches/export.sh` in the same iteration.

Run from `build/` with the validated route and canonical Start schedule; phase
gate on VI 512 via `probe.sh`, use a non-dot-prefixed capture path, and kill
with SIGKILL. Record the result in a new scratch evidence file, update the
ledger and CURRENT-TRUTH, then commit.
