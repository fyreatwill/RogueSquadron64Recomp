# M5 Session 3489 — non-ordinal selector-writer join

The prescribed keyed join used the retained independent retail capture from
Session 3487 and the qualified silent port capture from Session 3488. Both
captures had positive controls: the retail whole-RDRAM control reached its
threshold, while the port selector-writer and task-writer controls each fired.
The title key was normalized to origin `0x00790400`/`0x790400`, writer PC
`0x80091074`, selector value (`v0`), and operand-class fields (`a1`/`a2`);
separate runs were not joined by animation ordinal.

Retail produced 533 title rows, all with selector value `0x80171CE0`. The port
produced 1,024 rows: 512 with `0x80171CE0`, 511 with `0x80173B20`, and one with
`0x8018DD30`. The source-family key therefore has one retail family and three
port families, with the known family present on both routes and the latter
two present only on the port route. Operand-class joins do not remove this
source-family asymmetry: the `v0+a2` key has 16 common keys and 498 paired
rows, while the extra port source families remain unmatched.

This selects `H-WriterInputDivergence`: the first measured difference is the
selector/source value supplied to the common writer, not a later transform.
It rules out `H-SharedWriterTransform` at this boundary and leaves the
upstream selector/table producer unresolved. `H-KeyInsufficient` is not
selected because the source-family key yields a qualified overlap and a
route-exclusive class while both controls fired.

ORIGIN: diagnostic-only parsing of existing retail and port rows; no selector
or task field was rewritten, skipped, or validated.

Evidence: `scratch/agent/s3487_oracle_writer.log` and
`scratch/agent/s3488_m5_audio_disabled/run.log`.
