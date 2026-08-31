# NEXT work unit — trace the zero PCM RSP-DMA source edge

HYPOTHESIS-ID: m5-port-zero-pcm-source

The corrected s3375 port run reached both target phases with live host/task,
PCM, and filter controls. Its guest-store census found no primary-span store,
while RSP-DMA writes into the PCM ring were active with zero payload. Retail
ground truth independently shows guest `0x800078EC` writing each primary span
with nonzero values. The next question is where the zero enters the port's RSP
DMA source path; do not modify output, waits, slots, status, or consumer
dispatch.

Competing hypotheses:

- `H-PortRSPSourceZero`: the port's RSP DMEM/input source is already zero
  before the ring-buffer DMA.
- `H-PortRSPTransformZero`: the RSP source is nonzero, but the active RSP
  transform emits a zero output.
- `H-PortDMADestinationMismatch`: the observed zero DMA is not the PCM source
  span consumed by the audio callback.

Discriminating measurement: instrument one active factor5 audio task so the
same DMA event reports source-DMEM FNV/nonzero, post-transform DMEM
FNV/nonzero, and destination span, with the existing PCM source/consumer
joins and positive controls in the same run. Source zero selects
`H-PortRSPSourceZero`; nonzero source plus zero post-transform selects
`H-PortRSPTransformZero`; a destination outside the joined PCM span selects
`H-PortDMADestinationMismatch`.

Preparation: use the existing fixed port route and follow the regeneration
order. Ask the retail oracle for the whole-RDRAM control and matching primary
span writer rows before building the port instrument. Batch all source,
transform, destination, and join fields into one build and one run; positive
controls must include host/task/PCM plus title and hangar phase markers. Do not
change waits, slots, status handling, consumer dispatch, or PCM writeback until
the source boundary is named.
