# Next: expose input RDRAM-to-DMEM ordering

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3671 passed all drive/task controls, but the watched source-span rows
were `dmem_to_rdram` zero-payload writebacks. They do not measure the planned
input/source DMA, so the next unit must first expose the opposite direction in
the existing port instrumentation.

Competing hypotheses:

- H-InputDmaObserved: the existing hook can be phase-gated to report
  RDRAM-to-DMEM reads for the watched source span and can join them to task
  rows.
- H-OnlyWritebackObserved: the hook reports only DMEM-to-RDRAM writebacks;
  input ordering remains unavailable and needs a new hook.
- H-InputDmaZeroPayload: input reads are observed and carry zero payloads after
  the fixed zero-fill.
- H-CaptureInvalid: whole-RDRAM, title, hangar, or type-2 controls fail;
  discard the capture rather than interpreting a null.

Discriminating measurement: inspect the existing DMA hook's direction and
instrument one phase-gated table for both RDRAM-to-DMEM and DMEM-to-RDRAM
events, preserving source/destination, payload hash/nonzero count, task data
pointer, and route ordinal. Run one validated real-audio capture with the
whole-RDRAM, title, hangar, and type-2 controls. Input rows select
H-InputDmaObserved; only writeback rows select H-OnlyWritebackObserved; input
rows with zero payload select H-InputDmaZeroPayload. A missing control is
capture-invalid, not a null result.

Before building, read the relevant port instrumentation in
`docs/debug-trace-env-vars.md` and inspect the s3671 recipe. Build once, run
one 55-second validated real-audio capture from `build/`, and store the log
under `scratch/agent/` with a non-dot final component. No guest-state rewrite
or mitigation is in scope.
