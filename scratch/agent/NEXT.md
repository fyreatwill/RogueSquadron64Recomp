# NEXT work unit — qualify one source-payload writer edge

HYPOTHESIS-ID: m5-output-contract-boundary

Session 3536 showed task dispatch, image-stage routing, SP completion, and PCM
joins are live, but image-stage and PCM payloads are zero in both target
phases. Do not repeat the AI-return or broad task-route probe.

Next unit: add one batch instrument for a genuinely new source-payload writer
join, after checking retail watch capacity and candidate callsites. Use the
existing phase-keyed image-stage/PCM joins and independent retail ground truth
to name one writer PC, destination, and legitimate nonzero value. Do not
modify selector, task, or output state until that writer is selected.

Competing hypotheses and discriminator:

- `H-MissingOutputWriter`: retail has a phase-qualified writer/value edge that
  is absent or differs in the port, selecting the next contract change.
- `H-OutputParity`: retail and port both show the same legitimate nonzero
  source payload and ordering; Step 3 remains gated for a new discriminator.
- `H-OutputRouteMismatch`: the port reaches target phases but an output join is
  route-gated or ordered differently.
- `H-CaptureInvalid`: whole-RDRAM/port controls or a target phase is absent.

Required discriminator: one batch-instrumented, phase-keyed source-payload
writer table covering the existing dispatch, task, DMEM/DMA, image exit, SP
completion, service, slot/voice, MORT class, PCM source, and PCM consumer
joins, plus the new candidate writer PC/destination/value. Require the
independent retail whole-RDRAM control and a named writer/value before
selecting `H-MissingOutputWriter`.

Build/run shape: first inspect `tools/oracle/README.md` watch capacity and the
source-payload writer callsites; write the full candidate table before adding
the instrument. Build once and run phase-gated real-audio plus retail controls
in the same iteration. Do not repeat the silent arm or add a single-field
diagnostic.
