# Next work unit: M5 retail writer-family to port edge join

HYPOTHESIS-ID: m5-retail-writer-port-edge

Use s3767's fixed boundary: the image arm's `0x8008F2CC` clear is followed by
only zero target-span stores from `0x800078EC`, while retail independently
reaches title/hangar and writes both source ranges. Map the retail writer
families to the corresponding generated port callers/entries and compare
phase/order around the clear. Do not suppress or replace the clear.

Competing hypotheses:

- `H-M5-RetailWriterHasPortEdge`: each relevant retail writer family has a
  reachable, phase-matched port caller/entry that can be joined to the clear.
- `H-M5-RetailWriterPortEdgeAbsent`: at least one retail family has no
  corresponding port execution edge after the clear.
- `H-M5-RetailWriterJoinMismatch`: static addresses execute, but buffer,
  phase, or route identity prevents a valid retail-to-port join.

Discriminator: one phase-scoped table keyed by writer family containing the
retail writer PC/order, the generated port caller/entry, target buffer/range,
and phase/route identity. `HasPortEdge` requires matching buffer and phase;
`EdgeAbsent` requires a positive-control-backed missing family edge;
`JoinMismatch` requires execution without a valid identity join. Require the
oracle whole-RDRAM positive control and both title/hangar phases.

Exact commands:

`rg -n '80007670|8001E2C0|8001F|800078EC|8008F2CC' RecompiledFuncs src docs | head -200`

`grep -a -E '^\[(m5-static-rsmemset|field348-writer|m5-input-dma|audtask-image-stage|audtask-image-dma-join|audtask-join)' scratch/agent/s3767_m5_postclear_order/image.log | grep 'phase=5 width=512' | tail -240`

`grep -a -E '\[oracle\] (watch write|done:)|\[vi\].*origin=0x00(790400|6ab400)' scratch/agent/s3767_m5_postclear_order/oracle.log | tail -80`
