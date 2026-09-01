# NEXT work unit — qualify one image-task/output contract edge

HYPOTHESIS-ID: m5-output-contract-boundary

Session 3535 landed and validated the retail-equivalent `osAiSetFrequency`
actual-frequency contract. Do not repeat the AI-return probe.

Next unit: use the existing phase-keyed image-task/DMEM/DMA/PCM diagnostics and
independent retail ground truth to name one missing output contract edge. Do
not modify selector, task, or output state until a writer and legitimate value
are selected.

Competing hypotheses and discriminator:

- `H-MissingOutputWriter`: a retail-attributed writer/value/completion edge is
  absent or differs in the port, selecting the next contract change.
- `H-OutputParity`: task, DMEM/DMA, completion, and PCM joins match at the
  qualified scope; Step 3 remains gated for a new discriminator.
- `H-OutputRouteMismatch`: the port reaches target phases but an output join is
  route-gated or ordered differently.
- `H-CaptureInvalid`: whole-RDRAM/port controls or a target phase is absent.

Required discriminator: one batch-instrumented, phase-keyed comparison covering
dispatch, task fields/source, DMEM/DMA, image exit, SP completion, service,
slot/voice, MORT class, PCM source, and PCM consumer. Require an independent
retail control and a named writer/value before selecting `H-MissingOutputWriter`.

Build/run shape: first inspect the existing task/PCM instrumentation and
`tools/oracle/README.md` ground-truth capability; then build all required arms
in one build and run phase-gated real-audio plus retail controls. Do not repeat
the silent arm or add a single-field diagnostic.
