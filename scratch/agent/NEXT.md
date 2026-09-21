# Next: join dominant descriptor writers to logical task fields

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3661 completed the phase-gated writer census. Positive controls passed:
the oracle whole-RDRAM watch produced 194,936 writes and 1,610 valid phase
task rows; the port reached title and hangar with 3,582 ABI rows and 1,024
RSP-source rows. The result is mixed: active ranges share the
`0x80090DE4`-headed writer family, but title writes `0x173B20`/`0x173CB0`
while hangar writes `0x171E70`/`0x173CB0`; phase-inactive ranges remain
ambiguous between pre-phase initialization and another producer.

Next unit: one batched logical-argument census of the dominant retail writer
family (`0x80090DE4`, `0x80090AAC`, `0x80090AF4`, `0x80090B58`,
`0x80090CA4`, `0x80090DE4`, `0x80091078`, `0x8009114C`, `0x80091168`, and
`0x80091170`) using `--watch-pc`, `--pc-field-dump`, and the same four
descriptor watches/task dump. Keep title and hangar phase buckets and the
whole-RDRAM positive control. In the port, retain `audtask-abi`,
`audio-objects`, task/DMA, and RSP-source rows.

Competing hypotheses and discriminator:

- H-SharedLogicalProducer: the dominant PCs receive the same logical task or
  descriptor base and select different fields/ranges by phase. Expected:
  phase rows join to the same task/object arguments while destination offsets
  explain the active subset.
- H-PrePhaseInitialization: phase-inactive target ranges were initialized
  earlier. Expected: writer executions or field values occur before the title
  or hangar gate, with no matching target-phase task row.
- H-SeparateProducer: the active ranges are produced by distinct logical
  objects despite sharing some low-level PCs. Expected: writer argument
  fields separate by range/object after task-row joining.
- H-CaptureInvalid: expected only if whole-RDRAM, task, phase, or port controls
  fail; discard the census rather than infer ownership.

Discriminating outcome: a valid same-run join of writer PC, logical arguments,
destination range, and task row. One shared argument tuple with field-specific
destinations selects H-SharedLogicalProducer; pre-gate-only rows select
H-PrePhaseInitialization; separated tuples select H-SeparateProducer. Do not
add a writeback, zero-fill, guard, or game-state forcing.
