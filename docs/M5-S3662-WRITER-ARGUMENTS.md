# M5 Session 3662 — writer arguments joined to task fields

The batched retail-oracle/port census ran for 90 seconds with the whole-RDRAM
watch, four descriptor-range watches, the 10 requested writer-family PCs, the
type-2 task dump, and both title/hangar phase buckets. The port used the
rebuilt real-audio/LLE/spin-yield/autopilot route.

The positive controls passed: retail recorded 194,945 whole-RDRAM writes and
1,617 valid type-2 task rows with zero invalid pointers; the port reached title
`0x00790400`/1024 and hangar `0x006AB400`/512, with 3,519 ABI rows, 1,027
source rows, and 88 bounded audio-object rows.

The task dump produced one target tuple per phase: title rows used task
`0x80149470` with `data_ptr=0x80173B20` (627 rows), and hangar rows used the
same task with `data_ptr=0x80171E70` (990 rows). The writer-family field dump
joined the corresponding low-level argument: title executions had the
dominant writer chain's `$s1` at `0x80173B30`, while hangar executions had
`$s1` at `0x80171E80`. The family headed by `0x80090DE4` therefore receives a
phase-specific logical task descriptor and writes its field ranges relative to
that descriptor. The same-family executions and destination fields are not
evidence of a separate producer.

This selects `H-SharedLogicalProducer` and closes the current discriminator
between shared logical ownership and separate logical objects. It leaves the
phase-inactive ranges and the exact payload writer/source-DMA ordering open.
The 10-PC field dump also showed two requested PCs with zero executions
(`0x80090AF4`, `0x80091170`), so those are not promoted to producer evidence.

ORIGIN: diagnostic-only writer-argument and task joins; no guest or host value
was skipped, rewritten, or guarded.
