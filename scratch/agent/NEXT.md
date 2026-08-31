# NEXT work unit — qualify one M5 image task/output contract edge

HYPOTHESIS-ID: m5-contract-edge-qualification

The s3394 dual-origin repair is closed as unevaluable: the whole-RDRAM control
fired, but the long arm stopped before final summaries and the completion retry
stopped before the target phase. Do not repeat that oracle recipe. Perform one
bounded M5 contract-qualification experiment using the existing same-build
image/silent arms and current phase/task/PCM controls. Before any behavior
change, name one candidate edge from the checked-in task ABI and existing
evidence (writer, destination, legitimacy, and ordering).

Competing hypotheses:

- `H-ImageEdgeMissing`: the image arm has a specific missing task/output edge
  that can be implemented and validated without changing unrelated audio state.
- `H-ImageEdgePresent`: existing task/DMEM/DMA/SP/service/PCM controls already
  close the contract; no behavior change is justified.
- `H-PortBoundaryEarlier`: the missing edge is upstream of the observed port
  output span and cannot be selected from current port evidence.

Discriminator: both image and silent arms must reach title/hangar phase with
dispatch, task fields, DMEM/DMA, image exit, SP completion, service/slot, and
PCM controls. A named edge with independent retail evidence and matching port
ordering selects `H-ImageEdgeMissing`; all controls closing without a gap
selects `H-ImageEdgePresent`; a missing upstream producer with no legitimate
candidate selects `H-PortBoundaryEarlier`. Do not implement a contract edge in
this qualification unit.

Run from `build/` with the existing phase-qualified M5 A/B recipe and collect
both arms in one build/run; retain the whole-RDRAM oracle control before adding
any new port field. The candidate edge must be written into this file before
building. If no named edge can be supported, stop and record the specific
missing ground truth rather than adding instrumentation.
