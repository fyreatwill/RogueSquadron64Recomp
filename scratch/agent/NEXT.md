# NEXT work unit — design the non-ordinal selector-writer discriminator

HYPOTHESIS-ID: m5-task-field-writer

Session 3488 qualified the silent port route: title and hangar were reached,
the selector-writer control fired, and 1,024 writer rows were emitted without
a crash. The retained retail capture has 533 rows, so sequential ordinals are
not a valid cross-runtime key for the animated title scene.

Competing hypotheses and discriminating outcomes:

- `H-WriterInputDivergence`: a route-keyed selector/source class differs while
  both independent controls fire.
- `H-SharedWriterTransform`: route-keyed writer inputs match, but a later
  selector/output value class differs.
- `H-KeyInsufficient`: the proposed non-ordinal key yields no comparable
  rows despite positive controls, so the key—not the contract—is unresolved.

Discriminating measurement: construct one keyed table from the retained
retail rows and the Session 3488 port rows using title origin, writer PC,
selector value, and operand class—not ordinal or elapsed time. A class/value
match supports `H-SharedWriterTransform`; a class/value present only on one
route supports `H-WriterInputDivergence`; no qualified overlap supports
`H-KeyInsufficient` and requires a new key.

Expected command: use `awk`/`sort` over
`scratch/agent/s3487_oracle_writer.log` and
`scratch/agent/s3488_m5_audio_disabled/run.log` to emit the keyed tables and
their intersection/differences. No build or new runtime instrumentation is
needed until the key produces a qualified discriminator.
