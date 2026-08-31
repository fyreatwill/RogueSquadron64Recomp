# M5 s3401 — field348 input witness

The durable fixup now witnesses the store at guest PC `0x8008F2C8`, immediately
before the `0x8008F2CC` clear. It records the owning slot, stored pointer, and
phase while retaining the existing memset, image-stage, DMA, completion, and
PCM probes. The port binary rebuilt successfully.

The first paired attempt passed the retail oracle controls and reached hangar
only in the image arm; the silent arm crashed at the known scheduler boundary
(`spTaskSchedulerThread+9536`, guest PC `0x8000834c`). The image witness fired
in title and hangar: slot `0x80149764`, values `0x80178C80` and `0x801797B0`.
It also showed stage-3 zero output, but the pair was invalid because silent had
no target phase.

The immediate retry produced the complementary outcome: silent reached hangar
and emitted the same title/hangar input values, while image crashed at the same
scheduler boundary before phase instrumentation. The witness is therefore
live and repeatable, but no valid same-run silent/image discriminator was
obtained. No audio behavior changed.

Evidence: `scratch/agent/s3401_m5_field348_input/` and
`scratch/agent/s3401_m5_field348_input_retry/`.
