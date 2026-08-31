# NEXT work unit — reconcile the port producer witness with the indirect boundary

HYPOTHESIS-ID: m5-port-producer-boundary-reconciliation

Session 3407 passed the qualified port route in both arms but observed no
phase-qualified static-call row at `0x8002BEEC` or `0x800078EC`; image rows
were dominated by callsite `0x800052C4`. The host witness does not expose the
instruction-level indirect predecessor field.

Competing hypotheses:

- `H-PortBoundaryAbsent`: the port's observed translated producer route never
  reaches the retail boundary; the missing dispatch remains upstream.
- `H-PortBoundaryDifferent`: `0x800052C4` is a distinct translated producer
  route whose input/output contract differs from retail's indirect edge.
- `H-PortBoundaryInstrumentationGap`: the existing host witness cannot expose
  the relevant indirect predecessor, so the null is not yet an execution
  discriminator.

Discriminator: ask the retail oracle for `0x800052C4` execution and target-span
writes in the hangar bucket, with whole-RDRAM, title/hangar, and post-store
controls. A matching nonzero retail edge selects `H-PortBoundaryDifferent`;
no retail edge with controls live selects `H-PortBoundaryInstrumentationGap`;
a like-for-like edge selects `H-PortBoundaryAbsent` as a translated-route gap.
Do not add runtime instrumentation until the retail control names a measurable
field or PC.

Use one oracle run with whole-RDRAM, title/hangar, post-store, and the
`0x800052C4` execution/target controls. No port build is authorized until that
ground-truth arm passes and provides a discriminator. Do not alter waits,
slots, dispatch, or PCM writeback.
