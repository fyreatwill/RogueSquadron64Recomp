# M5 s3764 — image-task source/output boundary

The existing s3762 same-build oracle/image/silent capture was re-read; no
build or new instrument was used. The oracle whole-RDRAM control passed at
10,000 callbacks and all three arms reached title and hangar.

For the image arm's phase-5 hangar rows (`origin=0x6AB400`, `width=512`),
route ordinals, stage rows, DMA rows, and PCM rows align. At the input edge,
`m5-input-dma` reports `dram=0x1798B0`, `len=0x198`,
`input_fnv=0x762B22A5`, `input_nz=0`, and no previous writer. Image-stage
stage-2 and stage-3 rows preserve zero (`FNV=0xF59C39C5` and
`FNV=0x762B22A5`, respectively), and PCM source/consumer rows also remain
zero-valued.

This selects `H-M5-InputProducerGap` for the measured chain: the first
observed zero is already present at image-task input, before image-stage
transformation. It refutes `H-M5-OutputConsumerGap` for this chain and
`H-M5-Accounting` for these joined rows. This is single-capture evidence; it
does not identify the missing producer or authorize a writeback/fill
mitigation.

Evidence: `scratch/agent/s3762_m5_step1_silent_repeat/driver.log` and
`image.log`, especially route ordinals 659–664 and image-stage ordinals
660–664.
