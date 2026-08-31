# NEXT work unit — trace the zero-input caller contract

HYPOTHESIS-ID: m5-port-zero-pcm-source

Do exactly one bounded M5 caller/argument census next iteration. Do not modify output,
waits, slots, status handling, consumer dispatch, or PCM writeback.

Competing hypotheses:

- `H-PortSourceArgumentGap`: `rs_memset` receives a zero fill or source input
  before `0x800078EC` stores into the target span.
- `H-PortSourceCallerMismatch`: the port caller/callsite or buffer construction
  differs from retail even though the writer PC is the same.
- `H-PortSourceVisibility`: nonzero input reaches the writer but is lost
  between the writer and source DMA; current zero-store evidence disfavors it.

Discriminating measurement: first ask the retail oracle for the known writer's
caller/argument rows, with a whole-RDRAM positive control and canonical
title/hangar schedule. Then batch a phase-scoped port census of `rs_memset`
callsite, destination, fill/value, caller PC, and source-DMA route ordinal/row.
A zero fill before the stores selects `H-PortSourceArgumentGap`; a retail/
port callsite or destination mismatch selects `H-PortSourceCallerMismatch`;
nonzero input followed by zero stores selects a writer/ABI edge.

Before building, verify oracle watch indices and existing `rs_memset` caller
hooks. Keep phase, audio-task/ABI, PCM, image-stage/DMA, title, and hangar
controls live. If code under `lib/` changes, run
`./submodule-patches/export.sh` in the same iteration.

Run from `build/` with the validated route and canonical Start schedule; phase
gate on VI 512 via `probe.sh`, use a non-dot-prefixed capture path, and kill
with SIGKILL. Record the result in a new scratch evidence file, update the
ledger and CURRENT-TRUTH, then commit.
