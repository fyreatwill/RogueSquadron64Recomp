# Next: resolve phase-inactive descriptor ownership and payload ordering

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3662 selected `H-SharedLogicalProducer`: the retail task dump and
writer field dump joined title `data_ptr=0x80173B20` to writer `$s1=0x80173B30`
and hangar `data_ptr=0x80171E70` to `$s1=0x80171E80`. Controls passed: 194,945
whole-RDRAM writes, 1,617 valid type-2 task rows, title and hangar port VIs,
3,519 port ABI rows, and 1,027 source rows.

Next unit: one batched phase-gated retail caller/field census for the dominant
writer family and the four descriptor ranges, retaining the whole-RDRAM and
type-2 task controls. Add the writer `prev_pc`/`$ra` join and explicit
pre-phase buckets so the phase-inactive ranges can be separated into an
earlier initializer versus a different logical producer. Keep the port's
`audtask-abi`, task/DMA, RSP-source, and audio-object rows in the same paired
run. Use the existing validated route and SIGKILL watchdog.

Competing hypotheses and discriminator:

- H-PrePhaseInitialization: inactive ranges have writer/caller rows before
  their phase gate and no matching target-phase task tuple.
- H-SeparateLogicalProducer: inactive ranges have a distinct logical
  descriptor base or caller/`$ra` family, while active rows retain the s3662
  `data_ptr+0x10` join.
- H-SharedLogicalProducerAllPhases: the same task/caller argument family owns
  all four ranges, with inactive writes simply occurring before the phase
  bucket.
- H-CaptureInvalid: selected only if whole-RDRAM, task, phase, or port
  controls fail; discard the census rather than infer ownership.

Discriminating outcome: a valid same-run join of each range's writer PC,
caller/`$ra`, phase bucket, logical base, and task row. Pre-gate-only rows
select H-PrePhaseInitialization; a distinct base/caller selects
H-SeparateLogicalProducer; one shared task/caller family across pre- and
target-phase rows selects H-SharedLogicalProducerAllPhases. Do not add a
writeback, zero-fill, guard, or game-state forcing.
